# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, models

class report_product_sale_report_product_sale_template(models.AbstractModel):
    
    _name = 'report.product_sale.report_product_sale_template'
    
    @api.model
    def render_html(self, docids, data=None):        
        data = data if data is not None else {}
        start_date = data['form']['start_date']
        end_date = data['form']['end_date']
        docargs = {
            'doc_ids': data.get('ids', data.get('active_ids')),
            'data':{
                    'start_date' : data['form']['start_date'],
                    'end_date' : data['form']['end_date'],   
                    'data_list': data['dataline'] or [],
                    'total' : data['total'] or []              
                    }
            }
        return self.env['report'].render('product_sale.report_product_sale_template', docargs)