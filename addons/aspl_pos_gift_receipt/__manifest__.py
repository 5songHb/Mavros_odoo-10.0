# -*- coding: utf-8 -*-
#################################################################################
# Author      : Acespritech Solutions Pvt. Ltd. (<www.acespritech.com>)
# Copyright(c): 2012-Present Acespritech Solutions Pvt. Ltd.
# All Rights Reserved.
#
# This program is copyright property of the author mentioned above.
# You can`t redistribute it and/or modify it.
#
#################################################################################
{
    'name': 'POS Gift Receipt',
    'category': 'Point of Sale',
    'summary': 'This module allows user to print gift receipt along with payment receipt from pos interface.',
    'description': """
This module allows user to print gift receipt along with payment receipt from pos interface.
""",
    'author': 'Acespritech Solutions Pvt. Ltd.',
    'website': 'http://www.acespritech.com',
    'price': 25.00,
    'currency': 'EUR',
    'version': '1.0.1',
    'depends': ['base', 'point_of_sale'],
    'images': ['static/description/main_screenshot.png'],
    "data": [
        'views/point_of_sale.xml',
        'views/aspl_pos_gift_receipt.xml'
    ],
    'qweb': ['static/src/xml/pos.xml'],
    'installable': True,
    'auto_install': False,
    "application": True,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: