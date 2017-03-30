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
    def comput_search_qty_base_on_location(self):
        for each in self:
            for ware in self.env['stock.warehouse'].search([]):
                if each.id:
                    ctx = {'warehouse': ware.id, 'product_id': each.id}
                compute_qty = each.with_context(ctx)._compute_quantities_dict()
                for loc_id,value in compute_qty.items():
                        location_name = ware.lot_stock_id.customise_name
                        if location_name:
                            customise_name = location_name.upper()
                            if customise_name.startswith('STR'):
                                each.str_qty = value.get('qty_available')
                            elif customise_name.startswith('KAZ'):
                                each.kaz_qty = value.get('qty_available')
                            elif customise_name.startswith('LED'):
                                each.led_qty = value.get('qty_available')

    str_qty = fields.Integer("STR Qty" , compute = comput_search_qty_base_on_location)
    kaz_qty = fields.Integer("KAZ Qty" , compute = comput_search_qty_base_on_location)
    led_qty = fields.Integer("LED Qty" , compute = comput_search_qty_base_on_location)

class product_product(models.Model):
    _inherit = 'product.product'

    @api.multi
    def comput_search_qty_base_on_location(self):
        for each in self:
            for ware in self.env['stock.warehouse'].search([]):
                if each.id:
                    ctx = {'warehouse': ware.id, 'product_id': each.id}
                compute_qty = each.with_context(ctx)._compute_quantities_dict(lot_id=False, owner_id=False, package_id=False, from_date=False, to_date=False)
                for loc_id,value in compute_qty.items():
                        location_name = ware.lot_stock_id.customise_name
                        if location_name:
                            customise_name = location_name.upper()
                            if customise_name.startswith('STR'):
                                each.str_qty = value.get('qty_available')
                            elif customise_name.startswith('KAZ'):
                                each.kaz_qty = value.get('qty_available')
                            elif customise_name.startswith('LED'):
                                each.led_qty = value.get('qty_available')


    str_qty = fields.Integer("STR Qty" , compute = comput_search_qty_base_on_location)
    kaz_qty = fields.Integer("KAZ Qty" , compute = comput_search_qty_base_on_location)
    led_qty = fields.Integer("LED Qty" , compute = comput_search_qty_base_on_location)


class stock_location(models.Model):
    _inherit = "stock.location"

    customise_name = fields.Char("Customise Name")


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
