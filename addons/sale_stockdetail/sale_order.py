# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields,models,_,api

class sale_order_inher(models.Model):
    
    _inherit = "sale.order.line"
    
    @api.one
    @api.depends("product_id")
    def get_compute_stock(self):
        self.stock = self.product_id.qty_available
    
    @api.one
    @api.depends('order_id','order_id.warehouse_id')
    def get_location(self):
        if str(self.order_id.warehouse_id.lot_stock_id.name_get()[0][1]).lower().find('str') >= 0:
            self.is_str = True
        if str(self.order_id.warehouse_id.lot_stock_id.name_get()[0][1]).lower().find('kaz') >= 0:
            self.is_kaz = True
        if str(self.order_id.warehouse_id.lot_stock_id.name_get()[0][1]).lower().find('led') >= 0:
            self.is_led = True
        if str(self.order_id.warehouse_id.lot_stock_id.name_get()[0][1]).lower().find('chr') >= 0:
            self.is_chr = True
            
    @api.one
    @api.depends("product_id")
    def get_loc_stock(self):
        locations = self.env['stock.location'].search([('usage','=','internal')])
        location_ids = [location.id for location in locations]
        for l in locations:
            total = 0
            quant_ids = self.env['stock.quant'].search([('product_id','=',self.product_id.id),('location_id','=',l.id)])
            for q in quant_ids:
                total += q.qty
            if str(l.name_get()[0][1]).lower().find("str") >= 0:
                self.str = total
            if str(l.name_get()[0][1]).lower().find("kaz") >= 0:
                self.kaz = total
            if str(l.name_get()[0][1]).lower().find("led") >= 0:
                self.led = total
            if str(l.name_get()[0][1]).lower().find("chr") >= 0:
                self.chr = total
            if self.order_id.warehouse_id.lot_stock_id.id == l.id:
                self.whr = total
            
            
    stock = fields.Integer(compute=get_compute_stock,string="Total")
    str = fields.Integer(compute=get_loc_stock,string="str")
    kaz = fields.Integer(compute=get_loc_stock,string="kaz")
    led = fields.Integer(compute=get_loc_stock,string="led")
    chr = fields.Integer(compute=get_loc_stock,string="chr")
    whr = fields.Integer(compute=get_loc_stock,string="Whr")
    is_str = fields.Boolean(compute=get_location,string="Is Str?",default=False)
    is_kaz = fields.Boolean(compute=get_location,string="Is Kaz?",default=False)
    is_led = fields.Boolean(compute=get_location,string="Is Led?",default=False)
    is_chr = fields.Boolean(compute=get_location,string="Is Chr?",default=False)
    