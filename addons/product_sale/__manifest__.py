# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name': "Product Sale Report",

    'summary': """
         Product Sale Report.""",

    'description': """
        This Module used to get report of product sale.
    """,

    'author': "JustCodify",
    'website': "http://www.justcodify.com",

    'category': 'Warehouse',
    'version': '0.1',

    'depends': ['point_of_sale','product_extends'],

    'data': [
             'pos_order_view.xml',
             'views/product_sale_template.xml',
             'views/product_sale_report.xml',   
             'wizard/product_sale_report_view.xml',
         #'views/stock_operation_view.xml',
    ],
}