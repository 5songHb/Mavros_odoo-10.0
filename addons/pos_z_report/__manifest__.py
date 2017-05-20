# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name': "POS Z Report",

    'summary': """
         POS Z Report.""",

    'description': """
        This Module used to get report of POS Z.
    """,

    'author': "JustCodify",
    'website': "http://www.justcodify.com",

    'category': 'POS',
    'version': '0.1',

    'depends': ['point_of_sale','product_extends'],

    'data': [
             'views/pos_z_template.xml',
             'views/pos_z_report.xml',   
             'wizard/pos_z_report_view.xml',
    ],
}