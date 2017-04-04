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

{
'name': 'Poduct Location Quantity',
'category': 'Product',
'version': '1.1',
'summary': 'Poduct Location Quantity',
'description': """Poduct Location Quantity""",
'author': 'Acespritech Solutions Pvt. Ltd.',
'website': 'http://www.acespritech.com',
'images': [],
'depends': ['base','stock'],
'data': [
    'views/product_location_qty.xml',
    
],
'demo': [],
'test': [],
'qweb': [],
'installable': True,
'auto_install': False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: