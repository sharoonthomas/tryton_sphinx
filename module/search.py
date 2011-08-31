# This file is part of Tryton.  The COPYRIGHT file at the top level of
# this repository contains the full copyright notices and license terms.
from datetime import datetime

from trytond.model import ModelSQL, ModelView, fields
from trytond.transaction import Transaction

from tryton_sphinx.utils import guess_xml_type


class Model(ModelSQL, ModelView):
    """Full Text Search Enabled Models"""
    _name = "search.model"
    _description = __doc__
    _inherits = {'ir.model': 'model'}

    model = fields.Many2One('ir.model', 'Model', required=True, select=1)

    #: The last updated date time is dependent on the current language
    last_updated = fields.Function(
        fields.DateTime('Last Updated'),
        'get_last_updated', setter='set_last_updated'
        )

    #: A trigger is created which automatically adds a record being deleted to
    #: the kill list. It is important to store the reference to the trigger
    #: so that it can be deleted if the model is ever removed from full text
    #: search indexing.
    delete_trigger = fields.Many2One(
        'ir.trigger', 'On Delete Trigger', readonly=True)

    def __init__(self):
        super(Model, self).__init__()
        self._sql_constraints.append(
            ('unique_model', 'UNIQUE(model)', 'Model already added to indexes')
            )

    def get_last_updated(self, ids, name):
        """Lookup the last_updated date based on the language and return that
        """
        model_update_obj = self.pool.get('search.model.update')

        result = {}.fromkeys(ids, False)
        for model_id in ids:
            rec_ids = model_update_obj.search([
                ('search_model', '=', model_id),
                ('language', '=', Transaction().language)
            ])
            if rec_ids:
                result[model_id] = model_update_obj.browse(rec_ids[0]).date
        return result

    def set_last_updated(self, ids, name, value):
        """Set the last_updated date based on language
        """
        model_update_obj = self.pool.get('search.model.update')

        for model_id in ids:
            rec_ids = model_update_obj.search([
                    ('search_model', '=', model_id),
                    ('language', '=', Transaction().language)
                ])
            if rec_ids:
                model_update_obj.write(rec_ids, {'date': value})
            else:
                model_update_obj.create({
                    'date': value,
                    'search_model': model_id,
                    })
        return True

    def create(self, values):
        """Override to create a :attr:`delete_trigger` automatically when a
        model is added to `search.model`s
        """
        trigger_obj = self.pool.get("ir.trigger")
        model_obj = self.pool.get("ir.model")

        search_model_id, = model_obj.search([("model", "=", self._name)])

        values['delete_trigger'] = trigger_obj.create({
            "name": "Search Kill List",
            "model": values["model"],
            "on_delete": True,
            "action_model": search_model_id,
            "action_function": "add_to_kill_list",
            "condition": "True",
        })
        return super(Model, self).create(values)

    def delete(self, ids):
        """Delete the :attr:`delete_trigger` of the record also when the 
        record is deleted
        """
        trigger_obj = self.pool.get("ir.trigger")

        triggers = [record.delete_trigger.id for record in self.browse(ids)]
        trigger_obj.delete(triggers)

        return super(Model, self).delete(ids)

    def add_to_kill_list(self, deleted_rec_ids, trigger_id):
        """Add the `deleted_rec_ids` to the `search.kill_list` model

        .. admonition::

            The calling trigger must be the automatically generated trigger
            function and not a user created one because any such trigger_id 
            cannot be matched to a `search.model` record

        :param deleted_rec_ids: A list of IDS of the records that have been
                                deleted
        :param trigger_id: The ID of the trigger which triggered this call
        """
        kill_list_obj = self.pool.get("search.kill_list")

        search_model_id, = self.search([('delete_trigger', '=', trigger_id)])
        search_model = self.browse(search_model_id)
        for record_id in deleted_rec_ids:
            kill_list_obj.create({
                'model': search_model.model.id,
                'record_id': record_id,
                })

    def stream_new_records(self, model, stream):
        """Writes XML documents of all the new records after the last udpate of
        the model to the given stream.

        :param model: BrowseRecord of `search.model` object
        :param stream: A file like stream with a write method implementing file
                       write API
        """
        model_object = self.pool.get(model.model.model)

        attributes = {}
        for name, field in model_object._columns.iteritems():
            if not field.select:
                continue
            try:
                attributes[name] = guess_xml_type(field)
            except ValueError:
                continue

        # Send the schema first
        stream.write("<sphinx:schema>")
        for name, type in attributes.iteritems():
            if type == 'field':
                stream.write(u'<sphinx:field name="%s"/>'% name)
            else:
                stream.write(
                        u'<sphinx:attr name="%s" type="%s"/>' % (name, type))
        stream.write("</sphinx:schema>")

        # Now read the records and stream that too
        fields = attributes.keys()

        clause = []
        if model.last_updated:
            #: If there is a last_updated date then pick up records
            clause = [
                'OR',
                ('create_date', '>=', model.last_updated),
                ('write_date', '>=', model.last_updated),
            ]

        record_count = model_object.search(clause, count=True)
        for batch_start in xrange(0, record_count, 100):
            ids = model_object.search(clause, offset=batch_start, limit=100)
            for record in model_object.browse(ids):
                stream.write(u'<sphinx:document id="%d">' % record.id)
                for field in fields:
                    stream.write(
                        u'<%s>%s</%s>' % (field, getattr(record, field), field)
                    )
                stream.write(u'</sphinx:document>')

    def stream_kill_list(self, model, stream):
        """Writes to the stream the list of records to kill

        :param model: BrowseRecord of `search.model` object
        :param stream: A file like stream with a write method implementing file
                       write API
        """
        kill_list_obj = self.pool.get('search.kill_list')

        ids = kill_list_obj.search([('model', '=', model.id)])
        if not ids:
            return

        stream.write("<sphinx:killlist>")
        for kill_record in kill_list_obj.browse(ids):
            stream.write("<id>%d</id>" % kill_record.record_id)
        stream.write("</sphinx:killlist>")

        # Now remove the records from the database
        kill_list_obj.delete(ids)

    def stream_xml(self, model_id, stream):
        """Writes to the stream the Schema, Document and Kill Lists.

        :param model_id: ID of `search.model` object
        :param stream: A file like stream with a write method implementing file
                       write API
        """
        model = self.browse(model_id)
        with Transaction().new_cursor() as transaction:
            # Execute in a different Transaction so that changes being too
            # long does not result in stale records and locks
            timestamp = datetime.today()

            stream.write('<?xml version="1.0" encoding="utf-8"?>')
            stream.write("<sphinx:docset>")
            self.stream_new_records(model, stream)
            self.stream_kill_list(model, stream)
            stream.write("</sphinx:docset>")

            # Update the last updated date
            self.write(model.id, {'last_updated': timestamp})
            transaction.cursor.commit()

Model()


class ModelUpdate(ModelSQL, ModelView):
    """Search Model Update records"""
    _name = 'search.model.update'

    search_model = fields.Many2One(
        'search.model', 'Search Model', required=True, readonly=True)
    date = fields.DateTime('Date', required=True, readonly=True)
    language = fields.Char('Language code', required=True, size=5)

    def __init__(self):
        super(ModelUpdate, self).__init__()
        self._sql_constraints.append(
            ('unique_model_language', 
             'UNIQUE(search_model, language)', 
             'Model/Language pair already exists')
            )


ModelUpdate()


class KillList(ModelSQL, ModelView):
    """ModelWise Kill List"""
    _name = "search.kill_list"
    _description = __doc__

    model = fields.Many2One('search.model', 'Model', readonly=True, select=1)
    record_id = fields.Integer('Record ID', readonly=True)

KillList()
