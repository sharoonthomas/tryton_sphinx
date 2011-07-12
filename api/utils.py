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


def iter_sql_models(pool):
    """Given a pool iterate over all models that inherit from ModelSQL

    :param pool: AN instance of init'ed `trytond.pool.Pool` for a DB
    """
    for model_name in pool.object_name_list():
        model_obj = pool.get(model_name)
        if isinstance(model_obj, ModelSQL):
            yield model_obj 
    raise StopIteration
