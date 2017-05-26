# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name': "Sale Stock Details",

    'summary': """
         Sale Stock Details.""",

    'description': """
        This Module used to show the stock detail on sale order line.
    """,

    'author': "JustCodify",
    'website': "http://www.justcodify.com",

    'category': 'Sale',
    'version': '0.1',

    'depends': ['sale_stock',],

    'data': [
             'wizard/all_stock_view.xml',
	     'sale_order_view.xml',
    ],
}
