# -*- coding: utf-8 -*-

from odoo import http
from odoo.http import request
from odoo.addons.web.controllers.main import serialize_exception, content_disposition
import base64
from datetime import datetime


class Binary(http.Controller):

    @http.route('/web/binary/download_document/SO', type='http', auth="user")
    @serialize_exception
    def download_so_lines(self, **kw):
        length = len(kw['obj'])
        ids = [int(x) for x in kw['obj'][1:length - 1].split(',')]
        order_line = request.env['sale.order'].browse(ids)
        res = order_line.print_report_excel_data()
        data = res and res[0] or ''
        filename = 'SO_'
        filename += ' ' + str(datetime.now())
        filecontent = base64.b64decode(data)
        if not filecontent:
            return request.not_found()
        else:
            return request.make_response(filecontent,
                            [('Content-Type', 'application/octet-stream'),
                             ('Content-Disposition', content_disposition(filename + '.xls'))])

    @http.route('/web/binary/download_document/PO', type='http', auth="user")
    @serialize_exception
    def download_po_lines(self, **kw):
        length = len(kw['obj'])
        ids = [int(x) for x in kw['obj'][1:length - 1].split(',')]
        order_line = request.env['purchase.order'].browse(ids)
        res = order_line.print_report_excel_data()
        data = res and res[0] or ''
        filename = 'PO_'
        filename += ' ' + str(datetime.now())
        filecontent = base64.b64decode(data)
        if not filecontent:
            return request.not_found()
        else:
            return request.make_response(filecontent,
                            [('Content-Type', 'application/octet-stream'),
                             ('Content-Disposition', content_disposition(filename + '.xls'))])

    @http.route('/web/binary/download_document/PICK', type='http', auth="user")
    @serialize_exception
    def download_transfer_lines(self, **kw):
        length = len(kw['obj'])
        ids = [int(x) for x in kw['obj'][1:length - 1].split(',')]
        picking = request.env['stock.picking'].browse(ids)
        res = picking.print_report_excel_data()
        data = res and res[0] or ''
        filename = 'Transfer_'
        filename += ' ' + str(datetime.now())
        filecontent = base64.b64decode(data)
        if not filecontent:
            return request.not_found()
        else:
            return request.make_response(filecontent,
                            [('Content-Type', 'application/octet-stream'),
                             ('Content-Disposition', content_disposition(filename + '.xls'))])
