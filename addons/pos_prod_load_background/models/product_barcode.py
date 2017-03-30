# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (c) 2013-Present Acespritech Solutions Pvt. Ltd. (<http://acespritech.com>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp import models, fields, api, _
from odoo.exceptions import ValidationError

class product_barcode(models.Model):
    _name = 'product.barcode'

    barcode_product = fields.Char('Barcode Product', required=True)
    product_tmpl_id = fields.Many2one('product.template', 'Product')
    # _sql_constraints = [('uniq_barcode_product', 'unique(barcode_product)', _("Product barcode should be unique."))]

    @api.multi
    @api.constrains('barcode_product')
    def uniq_barcode_product(self):
        is_exist = self.search([('barcode_product', '=', self.barcode_product), ('id', '!=', self.id)])
        if is_exist:
            raise ValidationError(_('Barcode is already exist in %s') % is_exist.product_tmpl_id.name)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: