# -*- coding: utf-8 -*-
{
    'name': "Import/Export Purchase Order Lines",
    'summary': """
        Import/Export Purchase Order Lines""",
    'description': """
       Import/Export Purchase Order Lines
    """,
    'author': "DRC Systems India Pvt. Ltd.",
    'website': "http://www.drcsystems.com/",
    'category': 'Purchases',
    'version': '0.1',
    'depends': ['purchase'],
    'images': ['static/description/import_export_wizard.png'],
    'data': [
        'security/ir.model.access.csv',
        'data/data.xml',
        'views/res_config_view.xml',
        'views/import_export_view.xml',
    ],
    'currency': 'EUR',
    'installble': True,
    'auto_install': False,
    'application': False,
    'price': 35,
}
