# -*- coding: utf-8 -*-

from odoo import models, api, fields
import base64
import xlwt
try:
    from cStringIO import StringIO
except:
    from StringIO import StringIO


class SaleOrderInherit(models.Model):
    _inherit = "sale.order"

    mail_sent = fields.Boolean(string="Logistics Sent", default=False)
    mail_date_time = fields.Datetime(string="Logistics Sent Date")

    @api.multi
    def print_report_excel_data(self):
        sheet_name = 'Sale Order Line'
        workbook = xlwt.Workbook()
        sheet = workbook.add_sheet('Sale Order Line')
        sheet.col(0).width = 256 * 20
        sheet.col(1).width = 256 * 20
        sheet.col(2).width = 256 * 20
        sheet.col(3).width = 256 * 30
        sheet.col(4).width = 256 * 20
        sheet.col(5).width = 256 * 20
        sheet.col(6).width = 256 * 40
        sheet.col(7).width = 256 * 15
        sheet.col(8).width = 256 * 30
        sheet.col(9).width = 256 * 20
        sheet.col(10).width = 256 * 30
        sheet.col(11).width = 256 * 20
        sheet.col(12).width = 256 * 30
        sheet.col(13).width = 256 * 30
        sheet.col(14).width = 256 * 20
        sheet.col(15).width = 256 * 30
        sheet.col(16).width = 256 * 15
        sheet.col(17).width = 256 * 20
        sheet.col(18).width = 256 * 15
        sheet.col(19).width = 256 * 15
        sheet.col(20).width = 256 * 15
        sheet.col(21).width = 256 * 20
        sheet.col(22).width = 256 * 20
        sheet.col(23).width = 256 * 20
        sheet.col(24).width = 256 * 40
        sheet.col(25).width = 256 * 20
        sheet.col(26).width = 256 * 30
        sheet.col(27).width = 256 * 30

        font = xlwt.Font()
        style = xlwt.XFStyle()
        style.font = font
        cell = xlwt.easyxf('font: bold on, height 200; align: horiz center;')
        center = xlwt.easyxf('align: horiz center; font: bold on,height 500;')

        sheet.write_merge(0, 2, 0, 27, 'Order Lines', center)
        sheet.write(4, 0, "Document Type", cell)
        sheet.write(4, 1, "Apothetis", cell)
        sheet.write(4, 2, "DocumentCode", cell)
        sheet.write(4, 3, "Translated Document Code", cell)
        sheet.write(4, 4, "Registration Date", cell)
        sheet.write(4, 5, "Customer Code", cell)
        sheet.write(4, 6, "Customer Name", cell)
        sheet.write(4, 7, "Ship Code", cell)
        sheet.write(4, 8, "Address", cell)
        sheet.write(4, 9, "City", cell)
        sheet.write(4, 10, "Area", cell)
        sheet.write(4, 11, "Postal Code", cell)
        sheet.write(4, 12, "ShippingMethodDescription", cell)
        sheet.write(4, 13, "PaymentMethodDescription", cell)
        sheet.write(4, 14, "CashOnDeliveryFlag", cell)
        sheet.write(4, 15, "DocumentComments", cell)
        sheet.write(4, 16, "LineGID", cell)
        sheet.write(4, 17, "ItemCode", cell)
        sheet.write(4, 18, "MUCode", cell)
        sheet.write(4, 19, "Quantity", cell)
        sheet.write(4, 20, "Price", cell)
        sheet.write(4, 21, "DeliveryDate", cell)
        sheet.write(4, 22, "ReadField", cell)
        sheet.write(4, 23, "ReadDate", cell)
        sheet.write(4, 24, "CustomerOrderNumber", cell)
        sheet.write(4, 25, "StepCode", cell)
        sheet.write(4, 26, "Tel", cell)
        sheet.write(4, 27, "Mobile", cell)
        count_paid = 5

        for order in self:
            cod = 'F'
            if order.carrier_id:
                if order.carrier_id.name.lower() == "Cash on Delivery":
                    cod = 'T'
            date_order = order.date_order
            if date_order:
                date_order = order.date_order.split(' ')[0]
            for line in order.order_line:
                if line.product_id.default_code:
                    default_code = "'" + line.product_id.default_code
                else:
                    default_code = ''
                sheet.write(count_paid, 0, 'SO')
                sheet.write(count_paid, 1, 'Mavros Ltd')
                sheet.write(count_paid, 2, order.name)
                sheet.write(count_paid, 4, date_order)
                sheet.write(count_paid, 5, order.partner_id.id)
                sheet.write(count_paid, 6, order.partner_id.name)
                sheet.write(count_paid, 7, order.partner_shipping_id.id)
                sheet.write(count_paid, 8, order.partner_shipping_id.street or '')
                sheet.write(count_paid, 9, order.partner_shipping_id.city or '')
                sheet.write(count_paid, 10, order.partner_shipping_id.street2 or '')
                sheet.write(count_paid, 11, order.partner_shipping_id.zip or '')
                sheet.write(count_paid, 12, order.carrier_id.name or '')
                sheet.write(count_paid, 14, cod)
                sheet.write(count_paid, 17, default_code)
                sheet.write(count_paid, 18, 'EA')
                sheet.write(count_paid, 19, line.product_uom_qty)
                sheet.write(count_paid, 21, date_order)
                sheet.write(count_paid, 24, order.client_order_ref or '')
                sheet.write(count_paid, 26, order.partner_shipping_id.phone or '')
                sheet.write(count_paid, 27, order.partner_shipping_id.mobile or '')
                count_paid += 1

        fp = StringIO()
        workbook.save(fp)
        fp.seek(0)
        data = fp.read()
        fp.close()
        return (base64.b64encode(data), sheet_name)

class PurchaseOrderInherit(models.Model):
    _inherit = "purchase.order"

    mail_sent = fields.Boolean(string="Logistics Sent", default=False)
    mail_date_time = fields.Datetime(string="Logistics Sent Date")

    @api.multi
    def print_report_excel_data(self):
        sheet_name = 'Purchase Order Line'
        workbook = xlwt.Workbook()
        sheet = workbook.add_sheet('Purchase Order Line')
        sheet.col(0).width = 256 * 20
        sheet.col(1).width = 256 * 20
        sheet.col(2).width = 256 * 20
        sheet.col(3).width = 256 * 30
        sheet.col(4).width = 256 * 20
        sheet.col(5).width = 256 * 20
        sheet.col(6).width = 256 * 40
        sheet.col(7).width = 256 * 40
        sheet.col(8).width = 256 * 40
        sheet.col(9).width = 256 * 15
        sheet.col(10).width = 256 * 30
        sheet.col(11).width = 256 * 20
        sheet.col(12).width = 256 * 30
        sheet.col(13).width = 256 * 30
        sheet.col(14).width = 256 * 30
        sheet.col(15).width = 256 * 30
        sheet.col(16).width = 256 * 20
        sheet.col(17).width = 256 * 30
        sheet.col(18).width = 256 * 15
        sheet.col(19).width = 256 * 20
        sheet.col(20).width = 256 * 15
        sheet.col(21).width = 256 * 15
        sheet.col(22).width = 256 * 15
        sheet.col(23).width = 256 * 20

        font = xlwt.Font()
        style = xlwt.XFStyle()
        style.font = font
        cell = xlwt.easyxf('font: bold on, height 200; align: horiz center;')
        center = xlwt.easyxf('align: horiz center; font: bold on,height 500;')

        sheet.write_merge(0, 2, 0, 23, 'Order Lines', center)
        sheet.write(4, 0, "Apothetis", cell)
        sheet.write(4, 1, "Code", cell)
        sheet.write(4, 2, "Description", cell)
        sheet.write(4, 3, "ShortDescription", cell)
        sheet.write(4, 4, "MUCode", cell)
        sheet.write(4, 5, "AltMUCode", cell)
        sheet.write(4, 6, "Relation", cell)
        sheet.write(4, 7, "CBM_Per_Cartoon", cell)
        sheet.write(4, 8, "Weight_Per_Cartoon", cell)
        sheet.write(4, 9, "SerialNumberFlag", cell)
        sheet.write(4, 10, "MainBarcode", cell)
        sheet.write(4, 11, "DocumentType", cell)
        sheet.write(4, 12, "DocumentCode", cell)
        sheet.write(4, 13, "TranslatedDocumentCode", cell)
        sheet.write(4, 14, "RegistrationDate", cell)
        sheet.write(4, 15, "SupplierCode", cell)
        sheet.write(4, 16, "Address", cell)
        sheet.write(4, 17, "City", cell)
        sheet.write(4, 18, "Area", cell)
        sheet.write(4, 19, "PostalCode", cell)
        sheet.write(4, 20, "LineGID", cell)
        sheet.write(4, 21, "MUCode", cell)
        sheet.write(4, 22, "Quantity", cell)
        sheet.write(4, 23, "DeliveryDate", cell)
        count_paid = 5

        for order in self:
            date_order = order.date_order
            date_planned = order.date_planned
            if date_order:
                date_order = date_order.split(' ')[0]
            if date_planned:
                date_planned = date_planned.split(' ')[0]
            for line in order.order_line:
                default_code = ''
                barcode = ''
                if line.product_id.default_code:
                    default_code = "'" + line.product_id.default_code
                if line.product_id.barcode:
                    barcode = "'" + line.product_id.barcode
                sheet.write(count_paid, 0, 'Mavros Ltd')
                sheet.write(count_paid, 1, default_code)
                sheet.write(count_paid, 2, line.product_id.name)
                sheet.write(count_paid, 3, line.product_id.name)
                sheet.write(count_paid, 4, 'EA')
                sheet.write(count_paid, 5, 'BOX')
                sheet.write(count_paid, 6, line.product_id.pack or '')
                sheet.write(count_paid, 7, line.product_id.cbm or '')
                sheet.write(count_paid, 10, barcode)
                sheet.write(count_paid, 11, 'PO')
                sheet.write(count_paid, 12, order.partner_ref or '')
                sheet.write(count_paid, 14, date_order)
                sheet.write(count_paid, 15, order.partner_id.id)
                sheet.write(count_paid, 21, 'EA')
                sheet.write(count_paid, 22, line.product_qty)
                sheet.write(count_paid, 23, date_planned)
                count_paid += 1

        fp = StringIO()
        workbook.save(fp)
        fp.seek(0)
        data = fp.read()
        fp.close()
        return (base64.b64encode(data), sheet_name)

class StockPickingInherit(models.Model):
    _inherit = "stock.picking"

    mail_sent = fields.Boolean(string="Logistics Sent", default=False)
    mail_date_time = fields.Datetime(string="Logistics Sent Date")

    @api.multi
    def print_report_excel_data(self):
        sheet_name = 'Transfers'
        workbook = xlwt.Workbook()
        sheet = workbook.add_sheet('Transfers')
        sheet.col(0).width = 256 * 20
        sheet.col(1).width = 256 * 20
        sheet.col(2).width = 256 * 20
        sheet.col(3).width = 256 * 30
        sheet.col(4).width = 256 * 30
        sheet.col(5).width = 256 * 20
        sheet.col(6).width = 256 * 40
        sheet.col(7).width = 256 * 15
        sheet.col(8).width = 256 * 30
        sheet.col(9).width = 256 * 20
        sheet.col(10).width = 256 * 30
        sheet.col(11).width = 256 * 20
        sheet.col(12).width = 256 * 30

        font = xlwt.Font()
        style = xlwt.XFStyle()
        style.font = font
        cell = xlwt.easyxf('font: bold on, height 200; align: horiz center;')
        center = xlwt.easyxf('align: horiz center; font: bold on,height 500;')

        sheet.write_merge(0, 2, 0, 12, 'Transfers', center)
        sheet.write(4, 0, "Apothetis", cell)
        sheet.write(4, 1, "Date", cell)
        sheet.write(4, 2, "DOC_NUM", cell)
        sheet.write(4, 3, "ITEM_CODE", cell)
        sheet.write(4, 4, "DESCRIPTION", cell)
        sheet.write(4, 5, "AltCode", cell)
        sheet.write(4, 6, "MUCode", cell)
        sheet.write(4, 7, "AltMUCode", cell)
        sheet.write(4, 8, "Relation", cell)
        sheet.write(4, 9, "QTY_TRFR", cell)
        sheet.write(4, 10, "FROM_AREA", cell)
        sheet.write(4, 11, "TO_AREA", cell)
        sheet.write(4, 12, "ShippingMethodDescription", cell)
        count_paid = 5

        for picking in self:
            min_date = picking.min_date
            if min_date:
                min_date = min_date.split(' ')[0]
            for line in picking.move_lines:
                default_code = ''
                barcode = ''
                if line.product_id.barcode:
                    barcode = "'" + line.product_id.barcode
                if line.product_id.default_code:
                    default_code = "'" + line.product_id.default_code
                sheet.write(count_paid, 0, 'Mavros Ltd')
                sheet.write(count_paid, 1, min_date)
                sheet.write(count_paid, 2, picking.name)
                sheet.write(count_paid, 3, default_code)
                sheet.write(count_paid, 4, line.product_id.name)
                sheet.write(count_paid, 5, barcode)
                sheet.write(count_paid, 6, 'EA')
                sheet.write(count_paid, 7, 'BOX')
                sheet.write(count_paid, 8, line.product_id.pack or '')
                sheet.write(count_paid, 9, line.product_uom_qty)
                sheet.write(count_paid, 10, picking.location_id.name)
                sheet.write(count_paid, 11, picking.location_dest_id.name)
                sheet.write(count_paid, 12, picking.carrier_id.name)
                count_paid += 1

        fp = StringIO()
        workbook.save(fp)
        fp.seek(0)
        data = fp.read()
        fp.close()
        return (base64.b64encode(data), sheet_name)
