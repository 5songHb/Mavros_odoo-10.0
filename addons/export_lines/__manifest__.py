# -*- coding: utf-8 -*-
{
    'name': "Export Sale, Purchase and Transfer Lines",
    'summary': """
        Export Sale, Purchase and Transfer Order Lines in excel report""",
    'description': """
       Export Sale, Purchase and Transfer Lines
    """,
    'author': "DRC Systems India Pvt. Ltd.",
    'website': "http://www.drcsystems.com/",
    'category': 'Sales',
    'version': '0.1',
    'depends': ['sale', 'purchase', 'stock'],
    'data': [
        'views/export_view.xml',
        'views/stock_warehouse_views.xml',
        'views/sale_views.xml',
        'views/purchase_views.xml'
    ],
    'currency': 'EUR',
    'installble': True,
    'auto_install': False,
    'application': False,
    'price': '',
}
