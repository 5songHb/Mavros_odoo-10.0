from openerp import fields, api, models
import json
import logging

_logger = logging.getLogger(__name__)


fields = [
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
    'tracking'
]
class product(models.Model):

    _inherit = "product.product"

    @api.multi
    def write(self, vals):
        res = super(product, self).write(vals)
        _logger.info('write')
        for record in self:
            vals = record.read(fields)[0]
            vals['price'] = vals['list_price']
            path_file = self.env['pos.auto.cache'].get_data_path('products.json')
            if path_file:
                with open(path_file) as data_file:
                    datas = json.load(data_file)
                    datas[str(record.id)] = vals
                    with open(path_file, 'w') as outfile:
                        json.dump(datas, outfile)
                        _logger.info('write updated to file')
        return res

    @api.multi
    def unlink(self):
        path_file = self.env['pos.auto.cache'].get_data_path('products.json')
        if path_file:
            for record in self:
                with open(path_file) as data_file:
                    datas = json.load(data_file)
                    del datas[str(record.id)]
                    with open(path_file, 'w') as outfile:
                        json.dump(datas, outfile)
                        _logger.info('unlink updated to file')
        return super(product, self).unlink()

    @api.model
    def create(self, vals):
        new_partner = super(product, self).create(vals)
        vals = new_partner.read(fields)[0]
        vals['price'] = vals['list_price']
        path_file = self.env['pos.auto.cache'].get_data_path('products.json')
        if path_file:
            with open(path_file) as data_file:
                datas = json.load(data_file)
                datas[str(new_partner.id)] = vals
                with open(path_file, 'w') as outfile:
                    json.dump(datas, outfile)
                    _logger.info('create updated to file')
        return new_partner




