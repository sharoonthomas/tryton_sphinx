# This file is part of Tryton.  The COPYRIGHT file at the top level of
# this repository contains the full copyright notices and license terms.
from trytond.model import ModelSQL, ModelView, fields


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

Model()


class KillList(ModelSQL, ModelView):
    """ModelWise Kill List"""
    _name = "search.kill_list"
    _description = __doc__

    model = fields.Many2One('search.model', 'Model', readonly=True, select=1)
    record_id = fields.Integer('Record ID', readonly=True)

KillList()
