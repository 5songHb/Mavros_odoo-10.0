from openerp import fields, api, models
import json
import logging

_logger = logging.getLogger(__name__)

fields = [
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
    'property_account_position_id'
]
class partner(models.Model):

    _inherit = "res.partner"

    @api.multi
    def write(self, vals):
        res = super(partner, self).write(vals)
        _logger.info('write')
        for record in self:
            vals = record.read(fields)[0]
            path_file = self.env['pos.auto.cache'].get_data_path('partners.json')
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
        path_file = self.env['pos.auto.cache'].get_data_path('partners.json')
        if path_file:
            for record in self:
                with open(path_file) as data_file:
                    datas = json.load(data_file)
                    del datas[str(record.id)]
                    with open(path_file, 'w') as outfile:
                        json.dump(datas, outfile)
                        _logger.info('unlink updated to file')
        return super(partner, self).unlink()

    @api.model
    def create(self, vals):
        new_partner = super(partner, self).create(vals)
        vals = new_partner.read(fields)[0]
        path_file = self.env['pos.auto.cache'].get_data_path('partners.json')
        if path_file:
            with open(path_file) as data_file:
                datas = json.load(data_file)
                datas[str(new_partner.id)] = vals
                with open(path_file, 'w') as outfile:
                    json.dump(datas, outfile)
                    _logger.info('create updated to file')
        return new_partner



