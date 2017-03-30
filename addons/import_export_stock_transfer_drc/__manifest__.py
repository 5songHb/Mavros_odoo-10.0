# -*- coding: utf-8 -*-
{
    'name': "Import/Export Stock Lines",
    'summary': """
        Import/Export Stock Lines""",
    'description': """
       Import/Export Stock Lines
    """,
    'author': "DRC Systems India Pvt. Ltd.",
    'website': "http://www.drcsystems.com/",
    'category': 'Inventory',
    'version': '0.1',
    'depends': ['stock'],
    'data': [
        'security/ir.model.access.csv',
        # 'data/data.xml',
        # 'views/res_config_view.xml',
        'views/import_export_view.xml',
    ],
    'installble': True,
    'auto_install': False,
    'application': False,
}
