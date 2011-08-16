# -*- coding: utf-8 -*-
"""
    utils

    Some random utils which dont fit anywhere

    :copyright: (c) 2011 by Douglas Morato
    :license: BSD, see LICENSE for more details.
"""
from trytond.model import ModelSQL
from trytond.model.fields import (Integer, BigInteger, Boolean, DateTime,
    Numeric, Float, Char, Text, Selection)


def guess_type(field):
    import warnings
    warnings.warn("guess_type is deprecated, use guess_sql_type instead")
    return guess_sql_type(field)

def guess_sql_type(field):
    """The function checks the field's type and decides the best possible
    sphinx attribute to use for the field type
    """
    if isinstance(field, (Integer, BigInteger)):
        # Even the integer field in python could go beyond what could be com-
        # prehended by sphinx. So safer to use Big Int
        return 'sql_attr_bigint'

    if isinstance(field, Boolean):
        return 'sql_attr_bool'

    if isinstance(field, DateTime):
        return 'sql_attr_timestamp'

    if isinstance(field, (Numeric, Float)):
        return 'sql_attr_float'

    if isinstance(field, (Char, Text, Selection)):
        return 'sql_field_string'

    raise ValueError("%s is not a type recognised by sphinx" % type(field))


def guess_xml_type(field):
    """The function checks the field's types and decided the best possible xml
    data type to use
    """
    if isinstance(field, (Integer, BigInteger)):
        # Even the integer field in python could go beyond what could be com-
        # prehended by sphinx. So safer to use Big Int
        return 'int'

    if isinstance(field, Boolean):
        return 'bool'

    if isinstance(field, DateTime):
        return 'timestamp'

    if isinstance(field, (Numeric, Float)):
        return 'float'

    if isinstance(field, (Char, Text, Selection)):
        return 'field'

    raise ValueError("%s is not a type recognised by sphinx" % type(field))


def iter_sql_models(pool):
    """Given a pool iterate over all models that inherit from ModelSQL

    :param pool: AN instance of init'ed `trytond.pool.Pool` for a DB
    """
    for model_name in pool.object_name_list():
        model_obj = pool.get(model_name)
        if isinstance(model_obj, ModelSQL):
            yield model_obj
    raise StopIteration


def stream_new_records(pool, model, stream):
    """Writes XML documents of all the new records after the last udpate of
    the model to the given stream.

    .. admonition::
        This method must be called within the context of a Tryton Transaction

    .. note::
        The pool must be initialised before this method is called

    :param pool: An instance of trytond.pool.Pool for a given Database
    :param model: BrowseRecord of `search.model` object
    :param stream: A file like stream with a write method implementing file
                   write API
    """
    model_object = pool.get(model.model.model)

    attributes = {}
    for name, field in model_object._columns.iteritems():
        if field.select != 1:
            continue
        try:
            attributes[name] = guess_type(field)
        except ValueError:
            continue

    # Send the schema first
    stream.write("<sphinx:schema>")
    for name, type in attributes.iter_items():
        if type == 'field':
            stream.write(u'<sphinx:field name="%s"/>'% name)
        else:
            stream.write(u'<sphinx:attr name="%s" type="%s"/>' % (name, type))
    stream.write("</sphinx:schema>")

    # Now read the records and stream that too
    fields = attributes.keys()
    for record in model.new_records(model):
        stream.write('<sphinx:document id="%d">' % record.id)
        for field in fields:
            stream.write(
                    u'<%s>%s</%s>' % (field, getattr(record, field), field)
            )
        stream.write('</sphinx:document>')


def stream_kill_list(pool, model, stream):
    """Writes to the stream the list of records to kill

    .. admonition::
        This method must be called within the context of a Tryton Transaction

    .. note::
        The pool must be initialised before this method is called

    :param pool: An instance of trytond.pool.Pool for a given Database
    :param model: BrowseRecord of `search.model` object
    :param stream: A file like stream with a write method implementing file
                   write API
    """
    kill_list_obj = pool.get('search.kill_list')

    ids = kill_list_obj.search([('model', '=', model.id)])
    if not ids:
        return

    stream.write("<sphinx:killlist>")
    for kill_record in kill_list_obj.browse(ids):
        stream.write("<id>%d</id>" % kill_record.record_id)
    stream.write("</sphinx:killlist>")

    # Now remove the records from the database
    kill_list_obj.delete(ids)
