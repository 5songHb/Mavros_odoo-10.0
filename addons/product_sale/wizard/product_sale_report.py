# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api
from datetime import date,datetime,timedelta

total_gp = 0.0
total_sale = 0.0
total_inv_cost = 0.0

class product_sale(models.TransientModel):
    
    _name = 'product.sale'
    
    def _default_current_year(self):
        year=datetime.today().year
        return year
    
    def _get_first_date(self):
        return date(date.today().year,1,1)   
    
    start_date = fields.Date("Start Date",default=_get_first_date,required=True)
    end_date = fields.Date('End Date',default=date.today(),required=True)
    all_supplier = fields.Boolean("All Supplier",default=True)
    supplier_ids = fields.Many2many("res.partner",'product_sale_rel','product_id','partner_id',domain=[('supplier','=',True)],string="Suppliers")
    all_customer = fields.Boolean("All Customer",default=True)
    customer_ids = fields.Many2many("res.partner",'product_sale_cus_rel','product_id','partner_id',domain=[('customer','=',True)],string="Customers")
    include_retail = fields.Boolean("Include Retail",default=True)
    include_wh = fields.Boolean("Include Wholesale",default=True)
    all_brand = fields.Boolean("All Brand",default=True)
    brand_ids = fields.Many2many("product.brand",'product_brand_rel','product_id','brand_id',string='Brands')
    all_year = fields.Boolean('All Year',default=True)
    year = fields.Char('Year(Manufacturer)',default=_default_current_year)
    level = fields.Selection([(1,1),(2,2),(3,3),(4,4)],string="Product Category Level",default=4,required=True)
    no_sale = fields.Boolean("Show products with no sale",default=False)
    
    @api.multi
    def print_report(self):
        datas = {'ids': self.env.context.get('active_ids', [])}
        res = self.read(['start_date', 'end_date', 'all_supplier', 'supplier_ids', 'all_customer', 'customer_ids','include_retail','level'])
        res = res and res[0] or {}
        datas['form'] = res
        datas['dataline'] = self.get_dataline()
        datas['total'] = [{'total_gp':total_gp,'total_sale':total_sale,'total_inv_cost':total_inv_cost}]
        return self.env['report'].get_action([],'product_sale.report_product_sale_template',data=datas)
    
    def get_all_child_categ(self,categ_id):
        all_list = []
        first_data = self.env['product.category'].search([('parent_id','=',categ_id)])
        for f in first_data:
            all_list.append(f.id)
            tmp_list = self.get_all_child_categ(f.id)
            for s in self.env['product.category'].search([('id','in',tmp_list)]):
                all_list.append(s.id)
        return all_list
    
    def get_dataline(self):
        global total_gp,total_inv_cost,total_sale
        categ_id_list = []
        prod_categ_ids = self.env['product.category'].search([('parent_id','=',False)])
        if self.level == 1:
            categ_id_list = [categ.id for categ in prod_categ_ids]
        if self.level == 2:
            for categ in prod_categ_ids:
                for ct in categ.child_id:
                    categ_id_list.append(ct.id)
        cat_lev_2= []
        if self.level == 3:
            for categ in prod_categ_ids:
                for cat in categ.child_id:
                    cat_lev_2.append(cat.id)
                    categ_id_list.append(cat.id)
                    if cat.child_id:
                        for ct in cat.child_id:
                            categ_id_list.append(ct.id)
        cat_lev_3 = []
        if self.level == 4:
            for categ in prod_categ_ids:
                for cat in categ.child_id:
                    cat_lev_2.append(cat.id)
                    categ_id_list.append(cat.id)
                    if cat.child_id:
                        for ct in cat.child_id:
                            cat_lev_3.append(ct.id)
                            categ_id_list.append(ct.id)
                            if ct.child_id:
                                for c in ct.child_id:
                                    categ_id_list.append(c.id)
        final_list = []
        final_dict = {}
        brand_list = []
        if not self.all_brand:
            brand_list = [brand.id for brand in self.brand_ids]
        customer_list = []
        if not self.all_customer:
            customer_list = [customer.id for customer in self.customer_ids]
        all_pos_order = []
        pos_data = self.env['pos.order'].search([])
        all_pos_order = [pos.name for pos in pos_data]
        final_gp = 0.0
        final_sale = 0.0
        inv_query_data1 = []
        pos_query_data1 = []
        if self.include_wh:
            if not customer_list: #T
                if all_pos_order:
                    self.env.cr.execute('select invl.product_id ,sum(invl.price_subtotal) as ivalue, sum(invl.quantity) as qty from account_invoice_line invl, account_invoice inv'\
    " where inv.id = invl.invoice_id and inv.state not in ('draft','cancel') and inv.type in ('out_invoice','out_refund') and (inv.origin not in %s or inv.origin is NULL) and inv.date>= %s and inv.date <=%s group by product_id ",([tuple(all_pos_order),self.start_date,self.end_date]))
                else:
                    self.env.cr.execute('select invl.product_id ,sum(invl.price_subtotal) as ivalue, sum(invl.quantity) as qty from account_invoice_line invl, account_invoice inv'\
    " where inv.id = invl.invoice_id and inv.state not in ('draft','cancel') and inv.type in ('out_invoice','out_refund') and inv.date>= %s and inv.date <=%s  group by product_id ",([self.start_date,self.end_date]))
            else:
                self.env.cr.execute('select invl.product_id ,sum(invl.price_subtotal) as ivalue, sum(invl.quantity) as qty from account_invoice_line invl, account_invoice inv'\
    " where inv.id = invl.invoice_id and inv.partner_id in %s and inv.state not in ('draft','cancel') and inv.type in ('out_invoice','out_refund') and (inv.origin not in %s or inv.origin is NULL) and inv.date>= %s and inv.date <=%s group by product_id ",([tuple(customer_list),tuple(all_pos_order),self.start_date,self.end_date]))
            inv_query_data1 = self.env.cr.fetchall()
            
        if self.include_retail:
            next_date = datetime.strptime(self.end_date, "%Y-%m-%d") + timedelta(days=1)
            if not customer_list: #T
               self.env.cr.execute('select posl.product_id ,sum(posl.price_subtotal) as ivalue, sum(posl.qty) as qty from pos_order_line posl, pos_order pos'\
" where pos.id = posl.order_id and pos.state not in ('draft','cancel') and pos.date_order >= %s and pos.date_order <=%s group by product_id ",([self.start_date,next_date]))
            else:
               self.env.cr.execute('select posl.product_id ,sum(posl.price_subtotal) as ivalue, sum(posl.qty) as qty from pos_order_line posl, pos_order pos'\
" where pos.id = posl.order_id and pos.partner_id in %s and pos.state not in ('draft','cancel') and pos.date_order >= %s and pos.date_order <= %s and group by product_id ",([tuple(customer_list),self.start_date,next_date]))
            pos_query_data1 = self.env.cr.fetchall()  
        product_dict1 = {}
        if inv_query_data1:            
            for inv in inv_query_data1:                
                product_dict1[inv[0]] = [inv[1],inv[2]]
        if pos_query_data1:
            for pos in pos_query_data1:
                if product_dict1.has_key(pos[0]):
                    product_dict1[pos[0]] = product_dict1[pos[0]] + [pos[1],pos[2]]
                else:
                    product_dict1[pos[0]] = [0,0,pos[1],pos[2]]
        for p in product_dict1:
            if len(product_dict1[p]) < 4:
                product_dict1[p] = product_dict1[p] + [0,0]
        for categ in categ_id_list:
            temp_dict = {
                         'categ_name': '',
                         'products' : [],
                         'total_gp' : 0,
                         'total_sale' : 0,
                         'total_inv_cost' : 0.0,
                         }
            product_list = []            
            child_categ = [categ]
            cat_data = self.env['product.category'].search([('id','=',categ)])
            temp_dict['categ_name'] = cat_data.name_get()[0][1]
            if self.level == 3:
                if cat_lev_2:
                    if categ not in cat_lev_2:
                        child_categ = child_categ + self.get_all_child_categ(categ)            
                else:
                    child_categ = child_categ + self.get_all_child_categ(categ)
            elif self.level == 4:
                if cat_lev_3:
                    if categ in cat_lev_3:
                        child_categ = child_categ + self.get_all_child_categ(categ)
                elif cat_lev_2:
                        child_categ = child_categ
                else:
                    child_categ = child_categ + self.get_all_child_categ(categ)
            else:
                child_categ = child_categ + self.get_all_child_categ(categ)
            supplier_list = []
            
            if not self.all_supplier:
                for sup in self.supplier_ids:
                    supplier_list.append(sup.id)
                self.env.cr.execute('with tmp_sup_prod_tmp(product_tmpl_id) as' \
                 ' (' \
                 ' select distinct product_tmpl_id from product_supplierinfo' \
                 ' where name in %s ' \
                 ' ) ' \
                 " select pp.id from product_product pp,product_template p " \
                 " INNER JOIN tmp_sup_prod_tmp ps on p.id = ps.product_tmpl_id " \
                 " where p.categ_id=%s and pp.product_tmpl_id = p.id ",(tuple(supplier_list),categ))
                query_data = self.env.cr.fetchall()
                qurry_product_list = []
                
                for query in query_data:
                    qurry_product_list.append(query[0])
                if not brand_list and self.all_year: #tt
                    products = self.env['product.product'].search([('id','in',qurry_product_list),('categ_id','in',child_categ)])
                elif not brand_list and not self.all_year: #tf
                    products = self.env['product.product'].search([('id','in',qurry_product_list),('categ_id','in',child_categ),('manufacturer','=',self.year)])
                elif brand_list and self.all_year: #ft
                    products = self.env['product.product'].search([('id','in',qurry_product_list),('categ_id','in',child_categ),('brand','in',brand_list)])
                elif brand_list and not self.all_year: #ff
                    products = self.env['product.product'].search([('id','in',qurry_product_list),('categ_id','in',child_categ),('brand','in',brand_list),('manufacturer','=',self.year)])
            else:
                if not brand_list and self.all_year: #tt
                    products = self.env['product.product'].search([('categ_id','in',child_categ)])
                elif not brand_list and not self.all_year: #tf
                    products = self.env['product.product'].search([('categ_id','in',child_categ),('manufacturer','=',self.year)])
                elif brand_list and self.all_year: #ft
                    products = self.env['product.product'].search([('categ_id','in',child_categ),('brand','in',brand_list)])
                elif brand_list and not self.all_year: #ff
                    products = self.env['product.product'].search([('categ_id','in',child_categ),('brand','in',brand_list),('manufacturer','=',self.year)])
            cat_gp = 0.0
            cat_sale = 0.0
            for product in products:
                if product_dict1.has_key(product.id):
                    product_dict = {
                                'name' : '-',
                                'code' : '-',
                                'wh' : '-',
                                'ret' : '-',
                                'str' : '-',
                                'kaz' : '-',
                                'led' : '-',
                                'total_stock' : 0,
                                'retail' : '-',
                                'advertized' : '-',
                                'brand' : '-',
                                'year' : '-',
                                'value' : 0 
                                }
                    
                    '''quantity of each location '''
                    locations = self.env['stock.location'].search([('usage','=','internal')])
                    location_ids = [location.id for location in locations]
                    self.env.cr.execute("select product_id, location_id ,sum(qty) from stock_quant where product_id=%s"\
                    ' and location_id in %s group by product_id,location_id ',([product.id,tuple(location_ids)]))
                    location_data = self.env.cr.fetchall()
                    if location_data:
                        product_dict.update({'str':location_data[0][2]})
                        product_dict.update({'total_stock': product_dict['total_stock']+location_data[0][2]})
                        if len(location_data) == 2:
                            product_dict.update({'kaz':location_data[1][2],})
                            product_dict.update({'total_stock': product_dict['total_stock']+location_data[1][2]})
                        if len(location_data) == 3:
                            product_dict.update({'led':location_data[2][2],'kaz':location_data[1][2],})
                            product_dict.update({'total_stock': product_dict['total_stock']+location_data[2][2]+location_data[1][2]})
                    if product_dict['total_stock'] == 0:
                        product_dict.update({'total_stock':'-'})
                    inv_query_data = []
                    pos_query_data = []
                    ''' sale details '''
                    if self.include_wh:
                        product_dict.update({'wh':product_dict1[product.id][1],'value':product_dict1[product.id][0]})
                    if self.include_retail:
                        product_dict.update({'ret':product_dict1[product.id][3],'value':product_dict1[product.id][2]})
                    if self.include_wh and not self.include_retail:
                        if product_dict['value']:
                            cat_sale += product_dict['value']
                            cat_gp += (product_dict['value'] - (product.standard_price * product_dict1[product.id][1]))
                    if not self.include_wh and self.include_retail:
                        if product_dict['value']:
                            cat_sale += product_dict['value']
                            cat_gp += (product_dict['value'] - (product.standard_price * product_dict1[product.id][3]))
                    if self.include_wh and self.include_retail:
                        # aadd valeee
                        product_dict.update({'value':(product_dict1[product.id][2] + product_dict1[product.id][0])})
                        if product_dict['value']:
                            cat_sale += product_dict['value']
                            cat_gp += (product_dict['value'] - (product.standard_price * (product_dict1[product.id][1] + product_dict1[product.id][3])))
                    
                    product_dict.update({'name': product.name})
                    product_dict.update({'code':product.default_code})                
                    product_dict.update({'retail':product.list_price})
                    if product.brand:
                        product_dict.update({'brand': product.brand.name})
                    if product.manufacturer:
                        product_dict.update({'year':product.manufacturer})
                    if not self.no_sale:
                        if product_dict['value'] > 0:
                            product_list.append(product_dict)
                    else:
                        product_list.append(product_dict)
            if product_list:
                temp_dict['total_gp'] = cat_gp
                temp_dict['total_sale'] = cat_sale
                if cat_sale > 0:
                    temp_dict['total_inv_cost'] = round((cat_gp/cat_sale)*100,2)
                else:
                    temp_dict['total_inv_cost'] = 0.0
                total_gp += temp_dict['total_gp']
                total_sale += temp_dict['total_sale']
                if total_sale > 0:
                    total_inv_cost = round((total_gp/total_sale)*100,2)
                temp_dict['products'] = product_list
                final_list.append(temp_dict)
        return final_list