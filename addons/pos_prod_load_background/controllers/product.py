# -*- encoding: utf-8 -*-
##############################################################################
# Copyright (c) 2013 - Present Acespritech Solutions Pvt. Ltd. All Rights Reserved  (<http://acespritech.com>)
# Author: <info@acespritech.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# A copy of the GNU General Public License is available at:
# <http://www.gnu.org/licenses/gpl.html>.
#
##############################################################################

from openerp import models, fields, api, _

class product_product(models.Model):
    _inherit = 'product.product'

    @api.model
    def calculate_product(self):
        self._cr.execute("""
                        SELECT count(id) FROM PRODUCT_TEMPLATE where available_in_pos='t' and sale_ok='t'
                        """)
        total_product = self._cr.fetchall()
        return total_product

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: