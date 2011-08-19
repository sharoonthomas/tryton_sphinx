# This file is part of Tryton.  The COPYRIGHT file at the top level of
# this repository contains the full copyright notices and license terms.
from trytond.model import ModelSQL, ModelView, fields

from tryton_sphinx.utils import guess_xml_type


class Model(ModelSQL, ModelView):
    """Full Text Search Enabled Models"""
    _name = "search.model"
    _description = __doc__
    _inherits = {'ir.model': 'model'}

    model = fields.Many2One('ir.model', 'Model', required=True, select=1)
    last_updated = fields.DateTime('Last Updated', readonly=True, select=1)

    def __init__(self):
        super(Model, self).__init__()
        self._sql_constraints.append(
            ('unique_model', 'UNIQUE(model)', 'Model already added to indexes')
            )

    def create(self, values):
        # TODO: Create a trigger
        return super(Model, self).create(values)

    def delete(self, ids):
        # TODO: Delete the trigger created in :meth:`create`
        return super(Model, self).delete(ids)

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
        if search_model.last_updated:
            clause = [
                'OR',
                ('create_date', '>=', model.last_updated),
                ('write_date', '>=', model.last_updated),
            ]

        # TODO: Handle some kind of pagination here
        ids = model_obj.search(clause)
        for record in model_obj.browse(ids):
            stream.write('<sphinx:document id="%d">' % record.id)
            for field in fields:
                stream.write(
                        u'<%s>%s</%s>' % (field, getattr(record, field), field)
                )
            stream.write('</sphinx:document>')

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


class KillList(ModelSQL, ModelView):
    """ModelWise Kill List"""
    _name = "search.kill_list"
    _description = __doc__

    model = fields.Many2One('search.model', 'Model', readonly=True, select=1)
    record_id = fields.Integer('Record ID', readonly=True)

KillList()
