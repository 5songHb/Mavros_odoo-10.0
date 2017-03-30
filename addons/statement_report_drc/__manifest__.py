# -*- coding: utf-8 -*-
{
    'name': "Statement Report DRC",
    'summary': """
        Statement Report DRC""",
    'description': """
        Statement Report DRC
    """,
    'author': "DRC Systems India Pvt. Ltd.",
    'website': "http://www.drcsystems.com/",
    'category': 'Accounting',
    'version': '0.1',
    'depends': ['account', 'base'],
    'data': [
        'views/import_export_view.xml',
        'views/account_statement_report.xml',
        # 'views/partner_browser_statement_report.xml'
    ],
}
