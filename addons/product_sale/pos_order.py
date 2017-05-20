# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields,models,_,api

class pos_order_line(models.Model):
    
    _inherit = "pos.order.line"
    
    price_subtotal = fields.Float(compute='_compute_amount_line_all', digits=0, string='Subtotal w/o Tax',store=True)
    
class stock_quant_inherited(models.Model):
    
    _inherit = "stock.quant"
    
    inventory_value = fields.Float('Inventory Value', compute='_compute_inventory_value',store=False)
