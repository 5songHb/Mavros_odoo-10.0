# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError
from xlrd import open_workbook
try:
    from cStringIO import StringIO
except:
    from StringIO import StringIO
import base64
import xlwt
import datetime


class PurchaseOrderImportExport(models.Model):
    _name = "purchase.order.import.export.wizard"

    choose_file = fields.Binary('Choose File')
    filename = fields.Char('filename')
    active_id = fields.Many2one('purchase.order', default=lambda self: self._context.get('active_id'))
    is_validate = fields.Boolean(default=False)
    error = fields.Text('Error')
    is_error = fields.Boolean(default=False)

    @api.onchange('choose_file')
    def onchange_file(self):
        if self.choose_file:
            self.is_validate = False

    @api.multi
    def validate_file(self):
        message = ''
        if len(self._context.get('active_ids')) != 1:
            message = "You can import order lines in only one record."
        else:
            if self.choose_file:
                if self.active_id.state != 'draft':
                    message = 'You can import order lines only in case of when your Order is in "Draft" state.'
                else:
                    filename = str(self.filename)
                    if not (filename.endswith('xls') or filename.endswith('xlsx')):
                        message = "You can Import only '.xls' or '.xlsx' File."
                    else:
                        data_file = self.choose_file.decode('base64')
                        wb = open_workbook(file_contents=data_file)
                        cols = ['ID', 'NAME', 'CODE', 'QTY', 'PRICE']
                        data_cols = []
                        for s in wb.sheets():
                            for col in range(s.ncols):
                                if not message:
                                    value = (s.cell(0, col).value)
                                    if value.upper() in data_cols:
                                        message = "'" + value + "' columns is multiple time."
                                    else:
                                        data_cols.append(value.upper())
                        if not message:
                            for i in data_cols:
                                if not message:
                                    if i not in cols:
                                        message = "'" + i + "' is a invalid column name"
                            if 'ID' not in data_cols and not message:
                                if 'CODE' not in data_cols:
                                    message = "'Code' Column is mandatory"
            else:
                message = "please Select File."

        if not message:
            self.is_validate = True
            return {
                    'name': _(u'Import/Export Purchase Order Lines'),
                    'type': 'ir.actions.act_window',
                    'view_type': 'form',
                    'view_mode': 'form',
                    'res_model': 'purchase.order.import.export.wizard',
                    'target': 'new',
                    'res_id': self.id,
                    'context': self.env.context,
                     }
        raise UserError(_(message))

    @api.multi
    def compute_price(self, product, quantity):
        po = self.active_id
        price_unit = 0.0
        seller = product._select_seller(partner_id=po.partner_id,
            quantity=quantity,
            date=po.date_order and po.date_order[:10])
        if not seller:
            price_unit = 0.0
        else:
            fpos = po.fiscal_position_id
            taxes_id = fpos.map_tax(product.supplier_taxes_id)
            price_unit = self.env['account.tax']._fix_tax_included_price(seller.price, product.supplier_taxes_id, taxes_id) if seller else 0.0
            if price_unit and seller and po.currency_id and seller.currency_id != po.currency_id:
                price_unit = seller.currency_id.compute(price_unit, po.currency_id)
            if seller and product.product_tmpl_id.uom_po_id and seller.product_uom != product.product_tmpl_id.uom_po_id:
                price_unit = seller.product_uom._compute_price(price_unit, product.product_tmpl_id.uom_po_id)
        return price_unit

    @api.multi
    def import_order_line(self):
        date = datetime.datetime.now().strftime('%Y-%m-%d')
        data_file = self.choose_file.decode('base64')
        wb = open_workbook(file_contents=data_file)
        data_cols = []
        default_qty = 0
        message = ''
        for s in wb.sheets():
            for row in range(s.nrows):
                data_row = []
                for col in range(s.ncols):
                    value = (s.cell(row, col).value)
                    if row == 0:
                        data_cols.append(value.upper())
                    else:
                        data_row.append(value)
                vals = {}
                if row != 0:
                    vals['price_unit'] = 0.0
                    if 'QTY' in data_cols:
                        vals['product_qty'] = data_row[data_cols.index('QTY')]
                    else:
                        vals['product_qty'] = int(default_qty)
                    if 'NAME' in data_cols:
                        vals['name'] = data_row[data_cols.index('NAME')]
                    if 'PRICE' in data_cols and data_row[data_cols.index('PRICE')] != '':
                        vals['price_unit'] = data_row[data_cols.index('PRICE')]

                    if ('ID' not in data_cols) or ('ID' in data_cols and data_row[data_cols.index('ID')] == ''):
                        if str(data_row[data_cols.index('CODE')]):
                            if type(data_row[data_cols.index('CODE')]) == float:
                                code = str(int(data_row[data_cols.index('CODE')]))
                            else:
                                code = str(data_row[data_cols.index('CODE')])
                            product = self.env['product.product'].search([('default_code', '=', code)], limit=1)
                            if product:
                                if not vals.get('price_unit'):
                                    vals['price_unit'] = self.compute_price(product, vals['product_qty'])

                                vals.update({'order_id': self.active_id.id,
                                'product_id': product.id,
                                'date_planned': self.active_id.date_planned or date,
                                'product_uom': product.product_tmpl_id.uom_po_id.id})
                                if not vals.get('name'):
                                    vals['name'] = product.product_tmpl_id.description_purchase or product.name
                                self.env['purchase.order.line'].create(vals)
                            else:
                                message += "Product Code: " + str(data_row[data_cols.index('CODE')]) + " invalid at Row " + str(row) + " and Column " + str(col) + "\n"
                    else:
                        order_line = self.env['purchase.order.line'].search([('id', '=', int(data_row[0]))])
                        if order_line:
                            order_line.write(vals)
                        else:
                            message += "ID: " + str(int(data_row[data_cols.index('ID')])) + " invalid at Row " + str(row) + " and Column " + str(col) + "\n"
                else:
                    if 'QTY' not in data_cols:
                        default_qty = self.env['ir.config_parameter'].search([('key', '=', 'Defauly Qty To Import Product in Purchase Order')]).value

        if message:
            self.is_error = True
            self.error = message
            return {
                    'name': _(u'Import/Export Purchase Order Lines'),
                    'type': 'ir.actions.act_window',
                    'view_type': 'form',
                    'view_mode': 'form',
                    'res_model': 'purchase.order.import.export.wizard',
                    'target': 'new',
                    'res_id': self.id,
                    'context': self.env.context,
                     }

    @api.multi
    def print_report_excel_data(self):
        self.ensure_one()

        sheet_name = 'Purchase Order Line'
        workbook = xlwt.Workbook()
        sheet = workbook.add_sheet('Purchase Order Line 1')
        sheet.col(0).width = 256 * 35
        sheet.col(1).width = 256 * 20
        sheet.col(2).width = 256 * 20
        sheet.col(3).width = 256 * 40
        sheet.col(4).width = 256 * 20
        sheet.col(5).width = 256 * 20

        font = xlwt.Font()
        style = xlwt.XFStyle()
        style.font = font
        heading = xlwt.easyxf('font: bold on, height 300; align: horiz center;')
        bold = xlwt.easyxf('font: bold on')
        cell = xlwt.easyxf('font: bold on, height 200; align: horiz center;')
        total = xlwt.easyxf('font: bold on, height 220; align: horiz right;')
        center = xlwt.easyxf('align: horiz center;')

        sheet.write(0, 0, "ID", cell)
        sheet.write(0, 1, "Code", cell)
        sheet.write(0, 2, "Name", cell)
        sheet.write(0, 3, "Qty", cell)
        sheet.write(0, 4, "Price", cell)
        count_paid = 1

        lines = []
        for line in self.active_id.order_line:
            sheet.write(count_paid, 0, line.id or '')
            sheet.write(count_paid, 1, line.product_id.default_code or '')
            sheet.write(count_paid, 2, line.name or '')
            sheet.write(count_paid, 3, line.product_qty or '')
            sheet.write(count_paid, 4, line.price_unit or '')
            count_paid += 1

        fp = StringIO()
        workbook.save(fp)
        fp.seek(0)
        data = fp.read()
        fp.close()
        return (base64.b64encode(data), sheet_name)

    @api.multi
    def export_order_line(self):
        if len(self._context.get('active_ids')) != 1:
            raise UserError(_("You can export order lines of only one record."))
        return {
                'type': 'ir.actions.act_url',
                'url': '/web/binary/download_document/PO/%s' % self.id,
                'target': 'self',
                }
