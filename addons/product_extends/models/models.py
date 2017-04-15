# -*- coding: utf-8 -*-

# from openerp import models, fields, api

import datetime
from odoo import api, fields, models
import odoo.addons.decimal_precision as dp

# class Product_Barcode(models.Model):
#     _name="product.barcode"

#     name = fields.Char('Product Barcode')
#     product_tempalte_barcode_id = fields.Many2one('product.template')
#     _sql_constraints = [('barcode_name_unique', 'unique(name)', 'Barcode  already exists')]

class product_template(models.Model):

    _name = "product.template"
    _inherit = 'product.template'
    _description = "Product Unit of Measure"

    def _default_current_year(self):
        year=datetime.datetime.today().year
        return year
        
    def _default_float_value(self):
        value=format(0, '.4f')
        print value
        return value
 
    @api.one
    @api.depends('barcode')
    def _compute_first_barcode(self):
        if self.barcode:
            self.first_barcode = self.barcode
            print self.first_barcode

    first_barcode = fields.Char(string='First Barcode',store=True, readonly=True, compute='_compute_first_barcode')
    manufacturer = fields.Char('Year',required=True,default=_default_current_year)
    brand = fields.Many2one('product.brand','Brand')
    category = fields.Selection([('summer','Summer'),('winter', 'Winter')],'Season')
    advertising = fields.Boolean('Advertised',default=False)
    counted = fields.Char('Last Counted On')
    original_price = fields.Float('Original Price')
    form_num = fields.Integer('Form Num')
    pack = fields.Integer('Pack')
    cbm = fields.Char('CBM',default=_default_float_value)
    pack_inner = fields.Integer('Pack Inner')
    ytd_sales_retail = fields.Integer('YTD Sales Retail')
    ytd_wholesales = fields.Integer('YTD Wholesales')
    barcode_carton = fields.Char('Barcode Carton')
    product_barcodes = fields.Many2many('product.barcode', 'product_barcode_rel', 'product_barcode_rel_id1', 'product_barcode_rel_id2', 'Product Barcodes')
    # bar_code_ids = fields.One2many('product.barcode','product_tempalte_barcode_id',string="Multiple barcodes")

    def first_barcode_generator(self):
        print ("Calling Scheduler")
        search_product_ids = self.search([])
        for search_product_id in search_product_ids:
            try:
                print search_product_id
                temp_product = self.browse(search_product_id.id)
                print temp_product
                if temp_product.barcode:
                    temp_product.first_barcode = temp_product.barcode[:14]
                print temp_product.first_barcode
            except Exception:
                print ("Error")
                continue

class SaleOrderLine(models.Model):

    _inherit = 'sale.order.line'

    def count_sale_order_delivered_product(self):
        query = """SELECT product_id,sum(qty_delivered) as total from sale_order_line group by product_id order by product_id"""
        self.env.cr.execute(query)
        query_results = self.env.cr.dictfetchall()
        for index in range(0, len(query_results)):
            self.env['product.product'].search([('id','=',query_results[index].get('product_id'))]).write({
                'ytd_wholesales' : query_results[index].get('total')
                })
        
        query2 = """SELECT product_id,sum(qty) as total_qty from pos_order_line group by product_id order by product_id"""
        self.env.cr.execute(query2)
        query_results_2 = self.env.cr.dictfetchall()
        for index in range(0, len(query_results_2)):
            self.env['product.product'].search([('id','=',query_results_2[index].get('product_id'))]).write({
                'ytd_sales_retail' : query_results_2[index].get('total_qty')
                })

        return True

class Product_Brand(models.Model):

	_name ="product.brand"

	name = fields.Char('Brand Name',required=True)



	
class Partner(models.Model):

    _inherit= "res.partner"
    
    level = fields.Many2one('customer.level',string="Level")
    consignment_amount = fields.Integer("On Consignment Amount")
    credit_limit = fields.Float("Credit Limit")
    customer_children = fields.One2many('child.birtthday','partner_id',string="Children")
    customer_type = fields.Selection([('wholesale','Wholesale Customer'),('retail', 'Retail Customer')],'Customer Type')
    offer_type = fields.One2many('customer.group.discount','customer_offer_id',string='Discount Type')
    customer_form_num = fields.Char('Form Num')

    _defaults={

        'is_company':True,
    }



class Customer_Level(models.Model):

    _name="customer.level"
    

    name = fields.Char("Level name")


class Child_Birthday(models.Model):
    _name="child.birtthday"


    partner_id = fields.Many2one('res.partner',string="Customer Childrens")
    child_name = fields.Char("Child name")
    child_dob = fields.Date("Birthday")




class Customer_Group_Discount(models.Model):
    _name="customer.group.discount"


    customer_offer_id = fields.Many2one('res.partner',string="Customer Discounts")
    group_name = fields.Many2one('customer.group','Group name')
    discount = fields.Integer("Discount %")
    product_brand = fields.Many2one('product.brand','Product Brand')
    product_category = fields.Selection([('summer','Summer'),('winter', 'Winter')],'Product Category')

class Customer_Group(models.Model):
    _name = "customer.group"


    name = fields.Char("Group Name")
  
class Inventory(models.Model):
    _inherit = "stock.inventory"

    @api.multi
    def action_done(self):
        negative = next((line for line in self.mapped('line_ids') if line.product_qty < 0 and line.product_qty != line.theoretical_qty), False)
        if negative:
            raise UserError(_('You cannot set a negative product quantity in an inventory line:\n\t%s - qty: %s') % (negative.product_id.name, negative.product_qty))
        self.action_check()
        self.write({'state': 'done'})
        self.post_inventory()
        till_datetime = datetime.datetime.strptime(self.date,"%Y-%m-%d %H:%M:%S")
        till_datetime = till_datetime.strftime("%Y-%m-%d")
        for line in self.line_ids:
            line.product_id.id
            product_record=self.env['product.template'].search([('id', '=', line.product_id.id)])
            product_record.write({'counted': till_datetime+'/'+self.location_id.complete_name})
        return True


class SuppliferInfo(models.Model):
    _inherit = "product.supplierinfo"

    @api.multi
    def _compute_default_price(self):
        po_product_ids=self.env['purchase.order.line'].search([('product_id','=',self._context.get('default_product_tmpl_id'))])
        record_list=self.env['purchase.order.line'].browse(po_product_ids)
        value = 0.0
        if record_list:
            po_price_unit=record_list[-1].id.price_unit
            po_discount= record_list[-1].id.discount
            value = po_price_unit * (1- po_discount/100 )
            return value
        return value

    price = fields.Float(
        'Price', default=_compute_default_price, digits=dp.get_precision('Product Price'),
        required=True, help="The price to purchase a product")


   #Including the discount in Unit price in Product form 
class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    @api.multi
    def _add_supplier_to_product(self):
        # Add the partner in the supplier list of the product if the supplier is not registered for
        # this product. We limit to 10 the number of suppliers for a product to avoid the mess that
        # could be caused for some generic products ("Miscellaneous").
        for line in self.order_line:
            # Do not add a contact as a supplier
            partner = self.partner_id if not self.partner_id.parent_id else self.partner_id.parent_id
            if partner not in line.product_id.seller_ids.mapped('name') and len(line.product_id.seller_ids) <= 10:
                currency = partner.property_purchase_currency_id or self.env.user.company_id.currency_id
                supplierinfo = {
                    'name': partner.id,
                    'sequence': max(line.product_id.seller_ids.mapped('sequence')) + 1 if line.product_id.seller_ids else 1,
                    'product_uom': line.product_uom.id,
                    'min_qty': 0.0,
                    'price': self.currency_id.compute((line.price_unit*(1-(line.discount/100))), currency),
                    'currency_id': currency.id,
                    'delay': 0,
                }
                vals = {
                    'seller_ids': [(0, 0, supplierinfo)],
                    'manufacturer':datetime.datetime.today().year
                }
                try:
                    line.product_id.write(vals)
                except AccessError:  # no write access rights -> just ignore
                    break
# Removing the Internal Refernce from Purchase and Sale  in Product
# class ProductProduct(models.Model):
#     _inherit = "product.product"

#     @api.multi
#     def name_get(self):
#         # TDE: this could be cleaned a bit I think

#         def _name_get(d):
#             name = d.get('name', '')
#             code = self._context.get('display_default_code', True) and d.get('default_code', False) or False
#             # if code:
#             #     name = '[%s] %s' % (code,name)
#             return (d['id'], name)

#         partner_id = self._context.get('partner_id')
#         if partner_id:
#             partner_ids = [partner_id, self.env['res.partner'].browse(partner_id).commercial_partner_id.id]
#         else:
#             partner_ids = []

#         # all user don't have access to seller and partner
#         # check access and use superuser
#         self.check_access_rights("read")
#         self.check_access_rule("read")

#         result = []
#         for product in self.sudo():
#             # display only the attributes with multiple possible values on the template
#             variable_attributes = product.attribute_line_ids.filtered(lambda l: len(l.value_ids) > 1).mapped('attribute_id')
#             variant = product.attribute_value_ids._variant_name(variable_attributes)

#             name = variant and "%s (%s)" % (product.name, variant) or product.name
#             sellers = []
#             if partner_ids:
#                 sellers = [x for x in product.seller_ids if (x.name.id in partner_ids) and (x.product_id == product)]
#                 if not sellers:
#                     sellers = [x for x in product.seller_ids if (x.name.id in partner_ids) and not x.product_id]
#             if sellers:
#                 for s in sellers:
#                     seller_variant = s.product_name and (
#                         variant and "%s (%s)" % (s.product_name, variant) or s.product_name
#                         ) or False
#                     mydict = {
#                               'id': product.id,
#                               'name': seller_variant or name,
#                               'default_code': s.product_code or product.default_code,
#                               }
#                     temp = _name_get(mydict)
#                     if temp not in result:
#                         result.append(temp)
#             else:
#                 mydict = {
#                           'id': product.id,
#                           'name': name,
#                           'default_code': product.default_code,
#                           }
#                 result.append(_name_get(mydict))
#         return result


class AccountInvoiceLine(models.Model):
    _inherit = "account.invoice.line"


    @api.one
    @api.depends('price_unit', 'discount', 'invoice_line_tax_ids', 'quantity',
        'product_id', 'invoice_id.partner_id', 'invoice_id.currency_id', 'invoice_id.company_id')
    def _compute_price_unit_no_tax(self):
        self.price_unit_no_tax = self.price_unit / (1+(self.invoice_line_tax_ids.amount/100))
        print self.price_unit_no_tax
        # self.price_unit_no_tax = self.price_subtotal / self.quantity


    price_unit_no_tax = fields.Monetary(string='Unit Pice(No Tax)',
        store=True, readonly=True, compute='_compute_price_unit_no_tax')


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    @api.one
    @api.depends('product_uom_qty', 'discount', 'price_unit', 'tax_id')
    def _compute_price_unit_no_tax(self):
        self.price_unit_no_tax = self.price_unit / (1+(self.tax_id.amount/100))
        print self.price_unit_no_tax
        # self.price_unit_no_tax = self.price_subtotal / self.quantity


    price_unit_no_tax = fields.Monetary(string='Unit Pice(No Tax)',
        store=True, readonly=True, compute='_compute_price_unit_no_tax')

