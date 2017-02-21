# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Sale report',
    'version': '1.1',
    'category': 'Sale',
    'sequence': 150,
    'summary': 'Sale Report',
    'description': """
        Sale Report
    """,
    'website': 'https://www.odoo.com',
    'images': [],
    'depends': ['base','sale'],
    'data': [
              'sale_report_view.xml',
              ],
    'demo': [],
    'installable': True,
    'application': True,
    'auto_install': False,
    'qweb': [],
}
