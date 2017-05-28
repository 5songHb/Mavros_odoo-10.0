##############################################################################
#
# OpenERP, Open Source Management Solution
# Copyright (c) 2013-Present Acespritech Solutions Pvt. Ltd. (<http://acespritech.com>).
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp import models,fields,api,_


class product_template(models.Model):
    
    _inherit = 'product.template'

    @api.multi
    def _get_loc_stock(self):
        for each in self.search([]):
            self.env.cr.execute('with prodtmpl as'\
 '('\
 ' select pp.product_tmpl_id,pp.id from product_template pt'\
 ' inner join product_product pp on pp.product_tmpl_id = pt.id'\
 ' where pt.id = %s and pp.active = True'\
 ')'\
 ' select  p.product_tmpl_id,sum(s.qty),s.location_id from stock_quant s'\
 ' inner join prodtmpl p on p.id = s.product_id'\
 " inner join stock_location l on l.id = s.location_id and l.usage='internal'" \
 ' group by p.product_tmpl_id,s.location_id',(each.id,)
 )
            query_data = self.env.cr.fetchall()
            for query in query_data:
                locations = self.env['stock.location'].search([('usage','=','internal')])
                if locations:
                    for l in locations:
                        if query[2] == l.id:
                            if str(l.name_get()[0][1]).lower().find("str") >= 0:
                                each.str_qty = query[1]
                            if str(l.name_get()[0][1]).lower().find("kaz") >= 0:
                                each.kaz_qty = query[1]
                            if str(l.name_get()[0][1]).lower().find("led") >= 0:
                                each.led_qty = query[1]
                
    str_qty = fields.Integer("STR Qty" , compute=_get_loc_stock)
    kaz_qty = fields.Integer("KAZ Qty" , compute=_get_loc_stock)
    led_qty = fields.Integer("LED Qty" , compute=_get_loc_stock)

class product_product1(models.Model):
    
    _inherit = 'product.product'

    @api.multi
    def _get_loc_stock1(self):
        for each in self:
            locations = self.env['stock.location'].search([('usage','=','internal')])
            if locations:
                for l in locations:
                    total = 0
                    quant_ids = self.env['stock.quant'].search([('product_id','=',each.id),('location_id','=',l.id)])
                    for q in quant_ids:
                        total += q.qty
                    if str(l.name_get()[0][1]).lower().find("str") >= 0:
                        each.pstr_qty = total
                    if str(l.name_get()[0][1]).lower().find("kaz") >= 0:
                        each.pkaz_qty = total
                    if str(l.name_get()[0][1]).lower().find("led") >= 0:
                        each.pled_qty = total
                
    pstr_qty = fields.Integer("STR Qty" , compute=_get_loc_stock1)
    pkaz_qty = fields.Integer("KAZ Qty" , compute=_get_loc_stock1)
    pled_qty = fields.Integer("LED Qty" , compute=_get_loc_stock1)
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
