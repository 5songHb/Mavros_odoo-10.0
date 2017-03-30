# -*- coding: utf-8 -*-
from openerp import fields, models, api, _
import logging
import os
import time
import json

_logger = logging.getLogger(__name__)


class pos_auto_cache(models.TransientModel):
    _name = "pos.auto.cache"

    @api.model
    def get_products(self):
        _logger.info('>>>>>> start get_products')
        start_time = time.time()
        path_file = self.get_data_path('products.json')
        values = []
        if path_file:
            with open(path_file) as data_file:
                datas = json.load(data_file)
                for k, v in datas.iteritems():
                    values.append(v)
        _logger.info("--- %s seconds ---" % (time.time() - start_time))
        _logger.info('>>>>>> start get_products')
        return values

    @api.model
    def get_customers(self):
        _logger.info('>>>>>> start get_customers')
        start_time = time.time()
        path_file = self.get_data_path('partners.json')
        values = []
        if path_file:
            with open(path_file) as data_file:
                datas = json.load(data_file)
                for k, v in datas.iteritems():
                    values.append(v)
        _logger.info("--- %s seconds ---" % (time.time() - start_time))
        _logger.info('>>>>>> end get_customers')
        return values

    def get_data_path(self, filename):
        path = os.path.realpath(os.path.join(os.path.dirname(__file__), '..', 'datas'))
        return os.path.join(path, filename)

    @api.model
    def auto_cache(self):
        _logger.info('>>>>>> start auto_cache')
        start_time = time.time()
        partners = self.env['res.partner'].search([('customer', '=', True)])
        products = self.env['product.product'].search([('sale_ok', '=', True), ('available_in_pos', '=', True)])
        datas = {}
        for p in partners:
            datas[p.id] = p.read([
                'name',
                'street',
                'city',
                'state_id',
                'country_id',
                'vat',
                'phone',
                'zip',
                'mobile',
                'email',
                'barcode',
                'write_date',
                'id',
            ])[0]
        path_file = self.get_data_path('partners.json')
        with open(path_file, 'w') as outfile:
            json.dump(datas, outfile)
        _logger.info("--- cache partners need %s seconds ---" % (time.time() - start_time))
        datas = {}
        for p in products:
            datas[p.id] = p.read([
                'display_name',
                'list_price',
                'pos_categ_id',
                'taxes_id',
                'barcode',
                'default_code',
                'to_weight',
                'uom_id',
                'description_sale',
                'description',
                'product_tmpl_id',
                'id',
                'tracking',
            ])[0]
            datas[p.id]['price'] = datas[p.id]['list_price']
        path_file = self.get_data_path('products.json')
        with open(path_file, 'w') as outfile:
            json.dump(datas, outfile)
        _logger.info("--- cache product need %s seconds ---" % (time.time() - start_time))
        return True
