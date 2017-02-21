# -*- coding: utf-8 -*-

from odoo import models, fields

class StockWarehouse(models.Model):
    _inherit = "stock.warehouse"

    is_logistic = fields.Boolean(string="Is Logistic", default=False)
