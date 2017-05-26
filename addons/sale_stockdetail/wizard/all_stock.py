# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields,models,_,api

class total_stock(models.TransientModel):
    
    _name = 'total.stock'
    
    @api.one
    @api.depends('stock')
    def get_stock(self):
        so_data = self.env['sale.order.line'].search([('id','=',self._context['active_id'])])
        self.stock = so_data.stock
        self.str = so_data.str
        self.kaz = so_data.kaz
        self.led = so_data.led
        self.chr = so_data.chr
        
    stock = fields.Integer(compute=get_stock,string="Total",default=0)
    str = fields.Integer(compute=get_stock,string="str",default=0)
    kaz = fields.Integer(compute=get_stock,string="kaz",default=0)
    led = fields.Integer(compute=get_stock,string="led",default=0)
    chr = fields.Integer(compute=get_stock,string="chr",default=0)