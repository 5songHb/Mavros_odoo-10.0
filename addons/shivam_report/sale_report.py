# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from itertools import groupby
from datetime import datetime, timedelta

from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.tools import float_is_zero, float_compare, DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT
from odoo.tools.misc import formatLang

import odoo.addons.decimal_precision as dp

from dateutil import relativedelta
import time

from odoo.addons.procurement.models import procurement
from odoo.exceptions import UserError
from odoo.tools.float_utils import float_compare, float_round, float_is_zero


from odoo.tools import amount_to_text_en
from odoo.report import report_sxw
from xlwt import Workbook, XFStyle, Borders, Pattern, Font, Alignment,  easyxf
import os
import base64, urllib
import odoo.netsvc
import xlwt
from datetime import datetime
from odoo.osv import orm
from odoo.report import report_sxw
from odoo.addons.report_xls.report_xls import report_xls
from odoo.addons.report_xls.utils import rowcol_to_cell, _render
from odoo.tools.translate import translate, _
from odoo import pooler

import html2text

class SaleOrder(models.Model):
    _inherit = "sale.order"








_ir_translation_name = 'so.report.xls'

class _report_xls_parser(report_sxw.rml_parse):

    def __init__(self, cr, uid, name, context):
        super(so_report_xls_parser, self).__init__(cr, uid, name, context=context)
        wiz_obj = self.pool.get('sale.order')
        self.context = context
        wanted_list = wiz_obj._report_xls_so_report_fields(cr, uid, context)
        template_changes = wiz_obj._report_xls_template(cr, uid, context)
        self.localcontext.update({
            'datetime': datetime,
            'wanted_list': wanted_list,
            'template_changes': template_changes,
            '_': self._,
        })
        

    def _(self, src):
        lang = self.context.get('lang', 'en_US')
        return translate(self.cr, _ir_translation_name, 'report', lang, src) or src


class so_report_xls(report_xls):

    def __init__(self, name, table, rml=False, parser=False, header=True, store=False):
        super(so_report_xls, self).__init__(name, table, rml, parser, header, store)

        # Cell Styles
        _xs = self.xls_styles
        # header
        rh_cell_format = _xs['bold'] + _xs['fill'] + _xs['borders_all']
        self.rh_cell_style = xlwt.easyxf(rh_cell_format)
        self.rh_cell_style_center = xlwt.easyxf(rh_cell_format + _xs['center'])
        self.rh_cell_style_right = xlwt.easyxf(rh_cell_format + _xs['right'])
        # lines
        aml_cell_format = _xs['borders_all']
        self.aml_cell_style = xlwt.easyxf(aml_cell_format)
        self.aml_cell_style_center = xlwt.easyxf(aml_cell_format + _xs['center'])
        self.aml_cell_style_date = xlwt.easyxf(aml_cell_format + _xs['left'], num_format_str=report_xls.date_format)
        self.aml_cell_style_decimal = xlwt.easyxf(aml_cell_format + _xs['right'], num_format_str=report_xls.decimal_format)
        # totals
        rt_cell_format = _xs['bold'] + _xs['fill'] + _xs['borders_all']
        self.rt_cell_style = xlwt.easyxf(rt_cell_format)
        self.rt_cell_style_right = xlwt.easyxf(rt_cell_format + _xs['right'])
        self.rt_cell_style_decimal = xlwt.easyxf(rt_cell_format + _xs['right'], num_format_str=report_xls.decimal_format)

        # XLS Template
        self.col_specs_template = {
                                   
            'col1': {
                'header': [1, 30, 'text', _render("_('Employee Name')")],
                'lines': [1, 0, 'text', _render("''")],
                'totals': [1, 0, 'text', None]},    
            'col2': {
                'header': [1, 30, 'text', _render("_('Estimated Effort (Hrs.)')")],
                'lines': [1,0, 'text', _render("''")],
                'totals': [1, 0, 'text', None]},                               
            'col3': {
                'header': [1, 24, 'text', _render("_('Time Spent (Hrs.)')")],
                'lines': [1, 0, 'text',  _render("''")],
                'totals': [1,0, 'text', None]},                                                                                                                                  
                                   
                  
        }
      

    def generate_xls_report(self, _p, _xs, data, objects, wb):

        wanted_list = _p.wanted_list
        self.col_specs_template.update(_p.template_changes)
        _ = _p._

        wage_pos = 'wage' in wanted_list and wanted_list.index('wage')
        epf_deduction_pos = 'epf_deduction' in wanted_list and wanted_list.index('epf_deduction')
#         if not (credit_pos and debit_pos) and 'balance' in wanted_list:
#             raise oproject.task.report.wizardrm.except_orm(_('Customisation Error!'),
#                 _("The 'Balance' field is a calculated XLS field requiring the presence of the 'Debit' and 'Credit' fields !"))

        #report_name = objects[0]._description or objects[0]._name
        report_name = _("SO Report")
        ws = wb.add_sheet(report_name[:31])
        ws.panes_frozen = True
        ws.remove_splits = True
        ws.portrait = 0  # Landscape
        ws.fit_width_to_pages = 1
        row_pos = 0

        # set print header/footer
        ws.header_str = self.xls_headers['standard']
        ws.footer_str = self.xls_footers['standard']

        # Title
        cell_style = xlwt.easyxf(_xs['xls_title'])
        c_specs = [
            ('report_name', 1, 0, 'text', report_name),
         ]
        row_data = self.xls_row_template(c_specs, ['report_name'])
        row_pos = self.xls_write_row(ws, row_pos, row_data, row_style=cell_style)
#        row_pos += 1
        row_pos = 1
        
        # Column headers
        # c_specs = map(lambda x: self.render(x, self.col_specs_template, 'header', render_space={'_': _p._}), wanted_list)
        # row_data = self.xls_row_template(c_specs, [x[0] for x in c_specs])
        # row_pos = self.xls_write_row(ws, row_pos, row_data, row_style=self.rh_cell_style, set_column_size=True)
        # ws.set_horz_split_pos(row_pos)
#         row_data = self.xls_row_template(c_specs, _("Grand Total"))
#         print"-------------*************",ws, row_pos, row_data,cell_style
#         row_pos = self.xls_write_row(ws, row_pos, row_data, row_style=cell_style)
#         row_pos += 1
        # account move lines
        
        time_spent_total = 0.0
        planned_hrs_total = 0.0
        total_users = []
        task_work_ids = []
        task_list = []
        for line in objects:
            print"line===================",line,"object",objects
                
            c_specs = map(lambda x: self.render(x, self.col_specs_template, 'header', render_space={'_': _p._}), wanted_list)
            row_data = self.xls_row_template(c_specs, [x[0] for x in c_specs])
            row_pos = self.xls_write_row(ws, row_pos, row_data, row_style=self.rh_cell_style, set_column_size=True)
            ws.set_horz_split_pos(row_pos)


so_report_xls('so.report.xls',
    'sale.order',
    parser=so_report_xls_parser)







    



