# -*- coding: utf-8 -*-
#################################################################################
# Author      : Webkul Software Pvt. Ltd. (<https://webkul.com/>)
# Copyright(c): 2015-Present Webkul Software Pvt. Ltd.
# All Rights Reserved.
#
#
#
# This program is copyright property of the author mentioned above.
# You can`t redistribute it and/or modify it.
#
#
# You should have received a copy of the License along with this program.
# If not, see <https://store.webkul.com/license.html/>
#################################################################################
{
  "name"                 :  "Module For Merging Pos/Website Coupons",
  "summary"              :  "Module for merging POS/Website Coupons",
  "category"             :  "Accounting & Finance",
  "version"              :  "2.1",
  "sequence"             :  1,
  "author"               :  "Webkul Software Pvt. Ltd.",
  "website"              :  "https://store.webkul.com/Odoo.html",
  "description"          :  "",
  "live_test_url"        :  "http://odoodemo.webkul.com/?module=wk_coupons&version=10.0",
  "depends"              :  [
                             'sale',
                             'mail',
                            ],
  "data"                 :  [
                             'views/coupon_config_view.xml',
                             'views/wk_coupon_view.xml',
                             'views/coupon_history_view.xml',
                             'report/report.xml',
                             'report/report_template.xml',
                             'security/ir.model.access.csv',
                             'data/coupon_data_view.xml',
                             'data/mail_template.xml',
                             'wizard/wizard_view.xml',
                            ],
  "images"               :  ['static/description/Banner.png'],
  "application"          :  True,
  "installable"          :  True,
  "auto_install"         :  False,
  "pre_init_hook"        :  "pre_init_check",
}