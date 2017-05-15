# coding: utf-8

from odoo import models, fields, api, _


class res_users(models.Model):
    _inherit = "res.users"

    default_warehouse = fields.Many2one('stock.warehouse', string='Default Warehouse')

    def __init__(self, pool, cr):
        init_res = super(res_users, self).__init__(pool, cr)
        self.SELF_WRITEABLE_FIELDS = list(self.SELF_WRITEABLE_FIELDS)
        self.SELF_WRITEABLE_FIELDS.append('default_warehouse')
        return init_res


class sale_order(models.Model):
    _inherit = "sale.order"

    @api.multi
    @api.onchange('user_id')
    def onchange_user_id(self):
        self.ensure_one()
        if self.user_id and self.user_id.default_warehouse:
            self.warehouse_id = self.user_id.default_warehouse
