# -*- coding: utf-8 -*-
"""
    utils

    Some random utils which dont fit anywhere

    :copyright: (c) 2011 by Douglas Morato
    :license: BSD, see LICENSE for more details.
"""
from trytond.model import ModelSQL
from trytond.model.fields import (Integer, BigInteger, Boolean, DateTime,
    Numeric, Float, Char, Text, Selection, Function)


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
    if isinstance(field, Function):
        # Function fields wrap a simple field which is available in attribute
        # _field of the class
        return guess_xml_type(field._field)

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


def iter_search_models(pool):
    """Given a pool iterate over all models that inherit from ModelSQL

    :param pool: AN instance of init'ed `trytond.pool.Pool` for a DB
    """
    search_model_obj = pool.get('search.model')

    ids = search_model_obj.search([])
    for model in search_model_obj.browse(ids):
        yield pool.get(model.model.model)
    raise StopIteration
