# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
import base64
import xlwt
from xlrd import open_workbook
from odoo.exceptions import UserError
try:
    from cStringIO import StringIO
except:
    from StringIO import StringIO


class SaleOrderWizard(models.Model):
    _name = "sale.order.import.export.wizard"

    choose_file = fields.Binary('Choose File')
    filename = fields.Char('filename')
    active_id = fields.Many2one('sale.order', default=lambda self: self._context.get('active_id'))
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
                        cols = ['ID', 'NAME', 'CODE', 'QTY', 'PRICE', 'DISCOUNT']
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
                    'name': _(u'Import/Export Sale Order Lines'),
                    'type': 'ir.actions.act_window',
                    'view_type': 'form',
                    'view_mode': 'form',
                    'res_model': 'sale.order.import.export.wizard',
                    'target': 'new',
                    'res_id': self.id,
                    'context': self.env.context,
                     }
        raise UserError(_(message))

    @api.multi
    def compute_price(self, product, quantity):
        so = self.active_id
        # price_unit = 0.0
        product = product.with_context(
            lang=so.partner_id.lang,
            partner=so.partner_id.id,
            quantity=quantity,
            date=so.date_order,
            pricelist=so.pricelist_id.id,
        )
        if so.pricelist_id.discount_policy == 'without_discount':
            from_currency = so.company_id.currency_id
            price = from_currency.compute(product.lst_price, so.pricelist_id.currency_id)
        else:
            price = product.with_context(pricelist=so.pricelist_id.id).price
        # if so.pricelist_id and so.partner_id:
        #     price_unit = self.env['account.tax']._fix_tax_included_price(price, product.taxes_id, self.env['account.tax'])
        return price

    @api.multi
    def import_order_line(self):
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
                default_price = False
                if row != 0:
                    vals['price_unit'] = 0.0
                    if 'QTY' in data_cols:
                        vals['product_uom_qty'] = data_row[data_cols.index('QTY')]
                    else:
                        vals['product_uom_qty'] = int(default_qty)
                    if 'NAME' in data_cols:
                        vals['name'] = data_row[data_cols.index('NAME')]
                    if 'PRICE' in data_cols:
                        if data_row[data_cols.index('PRICE')] != '':
                            vals['price_unit'] = data_row[data_cols.index('PRICE')]
                    if 'DISCOUNT' in data_cols:
                        vals['discount'] = data_row[data_cols.index('DISCOUNT')]
                    if ('ID' not in data_cols) or ('ID' in data_cols and data_row[data_cols.index('ID')] == ''):
                        if str(data_row[data_cols.index('CODE')]):
                            if type(data_row[data_cols.index('CODE')]) == float:
                                code = str(int(data_row[data_cols.index('CODE')]))
                            else:
                                code = str(data_row[data_cols.index('CODE')])
                            product = self.env['product.product'].search([('default_code', '=', code)], limit=1)
                            if product:
                                vals['product_uom'] = product.product_tmpl_id.uom_id.id or False
                                if not vals['price_unit']:
                                    vals['price_unit'] = self.compute_price(product, vals['product_uom_qty'])
                                    default_price = True
                                vals.update({'order_id': self.active_id.id,
                                'product_id': product.id,
                                'product_uom': product.product_tmpl_id.uom_id.id or False})
                                if not vals.get('name'):
                                    description = ''
                                    if product.product_tmpl_id.description_sale:
                                        description = product.product_tmpl_id.description_sale
                                    vals['name'] = "[" + str(code) + "]" + product.name + ' ' + description
                                new_line = self.env['sale.order.line'].create(vals)
                                if not default_price:
                                    expected_subtotal = vals['price_unit'] * int(vals['product_uom_qty'])
                                    if not expected_subtotal == new_line.price_subtotal:
                                        price_difference = (expected_subtotal - new_line.price_subtotal) / int(vals['product_uom_qty'])
                                        new_line.write({'price_unit': vals['price_unit'] + price_difference})
                            else:
                                message += "Product Code: " + str(data_row[data_cols.index('CODE')]) + " invalid at Row " + str(row) + " and Column " + str(col) + "\n"
                    else:
                        order_line = self.env['sale.order.line'].search([('id', '=', int(data_row[0]))])
                        if order_line:
                            order_line.write(vals)
                            if not default_price:
                                new_line = order_line
                                expected_subtotal = vals['price_unit'] * int(vals['product_uom_qty'])
                                if not expected_subtotal == new_line.price_subtotal:
                                    price_difference = (expected_subtotal - new_line.price_subtotal) / int(vals['product_uom_qty'])
                                    new_line.write({'price_unit': vals['price_unit'] + price_difference})
                        else:
                            message += "ID: " + str(int(data_row[data_cols.index('ID')])) + " invalid at Row " + str(row) + " and Column " + str(col) + "\n"
                else:
                    if 'QTY' not in data_cols:
                        default_qty = self.env['ir.config_parameter'].search([('key', '=', 'Defauly Qty To Import Product in Sale Order')]).value
        if message:
            self.is_error = True
            self.error = message
            return {
                    'name': _(u'Import/Export Sale Order Lines'),
                    'type': 'ir.actions.act_window',
                    'view_type': 'form',
                    'view_mode': 'form',
                    'res_model': 'sale.order.import.export.wizard',
                    'target': 'new',
                    'res_id': self.id,
                    'context': self.env.context,
                     }

    @api.multi
    def print_report_excel_data(self):
        self.ensure_one()

        sheet_name = 'Sale Order Line'
        workbook = xlwt.Workbook()
        sheet = workbook.add_sheet('Sale Order Line 1')
        sheet.col(0).width = 256 * 35
        sheet.col(1).width = 256 * 20
        sheet.col(2).width = 256 * 20
        sheet.col(3).width = 256 * 40
        sheet.col(4).width = 256 * 20
        sheet.col(5).width = 256 * 20

        font = xlwt.Font()
        style = xlwt.XFStyle()
        style.font = font
        # heading = xlwt.easyxf('font: bold on, height 300; align: horiz center;')
        # bold = xlwt.easyxf('font: bold on')
        cell = xlwt.easyxf('font: bold on, height 200; align: horiz center;')
        # total = xlwt.easyxf('font: bold on, height 220; align: horiz right;')
        # center = xlwt.easyxf('align: horiz center;')

        sheet.write(0, 0, "ID", cell)
        sheet.write(0, 1, "Code", cell)
        sheet.write(0, 2, "Name", cell)
        sheet.write(0, 3, "Qty", cell)
        sheet.write(0, 4, "Price", cell)
        sheet.write(0, 5, "Discount", cell)
        count_paid = 1

        # lines = []
        for line in self.active_id.order_line:
            sheet.write(count_paid, 0, line.id or '')
            sheet.write(count_paid, 1, line.product_id.default_code or '')
            sheet.write(count_paid, 2, line.name or '')
            sheet.write(count_paid, 3, line.product_uom_qty or '')
            sheet.write(count_paid, 4, line.price_unit or '')
            sheet.write(count_paid, 5, line.discount or 0)
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
                'url': '/web/binary/download_document/SO/%s' % self.id,
                'target': 'self'
                }
