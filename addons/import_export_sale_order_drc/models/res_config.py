# -*- coding: utf-8 -*-

from odoo import api, fields, models

class sale_configuration(models.TransientModel):
    _inherit = 'sale.config.settings'

    group_import_order_line = fields.Boolean(string="Import Sale Order Line from Excel file?",
        implied_group='import_export_sale_order_drc.sale_group_impex_orderline')
