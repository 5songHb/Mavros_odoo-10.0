# -*- coding: utf-8 -*-
{
    'name': "Product Customisation",

    'summary': """
  Customisation for Product as per the requirements .""",

    'description': """
        This module contains all the extended customisation for the Project .
    """,

    'author': "Shivam Mahajan",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/openerp/addons/base/module/module_data.xml
    # for the full list
    'category': 'product',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','product','sale','purchase','account','stock','sale_margin'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/views.xml',
        

    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}