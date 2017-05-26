# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api
from datetime import date,datetime,timedelta
import decimal
import locale
locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')

class product_sale(models.TransientModel):
    
    _name = 'pos.z'
    
    date = fields.Date("Sale Date",default=date.today(),required=True)
    location_id = fields.Many2one("stock.location",string='Location',domain="[('usage','=','internal')]",required=True)
    
    @api.multi
    def print_report(self):        
        datas = {'ids': self.env.context.get('active_ids', [])}
        res = self.read(['date', 'location_id'])
        res = res and res[0] or {}
        datas['form'] = res
        datas['cashier_total'] = self.get_total()
        return self.env['report'].get_action([],'pos_z_report.report_pos_z',data=datas)
    
    def get_total(self):
        final_dict = {}
        location_pos = self.env['pos.config'].search([('stock_location_id','=',self.location_id.id)])
        total = 0.0
        loc_list = []
        
        for location in location_pos:
            loc = {}
            if not loc.has_key(location.id):
                loc.update({'id':location.id,'name':location.name,'total':0.0})
            next_date = (datetime.strptime(self.date, "%Y-%m-%d") + timedelta(days=1)).date().strftime("%Y-%m-%d")
            for order in self.env['pos.order'].search([('config_id','=',location.id),('date_order','>=',self.date),('date_order','<',next_date)]):
                loc['total'] += order.amount_total
                total += order.amount_total
            if loc['total'] > 0:
                loc_list.append(loc)
        for l in loc_list:
            if l['total'] >= 0:
                l['total'] = locale.currency(l['total'],grouping=True)[1:]
        if total >= 0:
            final_dict.update({'total':locale.currency(total,grouping=True)[1:],'cashier_total':loc_list})
        return final_dict