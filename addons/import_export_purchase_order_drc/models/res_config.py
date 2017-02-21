# -*- coding: utf-8 -*-

from odoo import api, fields, models

class purchase_config_settings(models.TransientModel):
    _inherit = 'purchase.config.settings'

    group_import_order_line = fields.Boolean(string="Import Purchase Order Line from Excel file?",
        implied_group='import_export_purchase_order_drc.purchase_group_impex_orderline')
