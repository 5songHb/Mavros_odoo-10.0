# -*- coding: utf-8 -*-
{
    'name': 'User Default Warehouse',
    'version': '1.1',
    'category': 'Warehouse',
    'summary': 'Default warehouse in sales order is taken from user settings',
    'description': '''
Default User Warehouse
======================
Warehouse in sales order is taken from user settings
----------------------------------------------------
* Allow users changing default warehouse in their preferences
* Change it by yourself in user settings
* When a salesperson is selected in a quotation, wharehouse is automatically entered
    ''',
    'price': '30.00',
    'currency': 'EUR',
    'auto_install': False,
    'application':True,
    'author': 'IT Libertas',
    'website': 'http://itlibertas.com',
    'depends': [
        'sale_stock',
    ],
    'data': [
        'views/user.xml',
        'data/data.xml',
        'security/ir.model.access.csv',
            ],
    'qweb': [

            ],
    'js': [

            ],
    'demo': [

            ],
    'test': [

            ],
    'license': 'Other proprietary',
    'images': ['static/description/main.png'],
    'update_xml': [],
    'application':True,
    'installable': True,
    'private_category':False,
    'external_dependencies': {
    },

}
