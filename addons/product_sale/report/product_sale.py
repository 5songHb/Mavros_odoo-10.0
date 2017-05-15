# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, models
from datetime import datetime

class report_product_sale_report_product_sale_template(models.AbstractModel):
    
    _name = 'report.product_sale.report_product_sale_template'
    
    @api.model
    def render_html(self, docids, data=None):        
        data = data if data is not None else {}
        start_date = datetime.strptime(str(data['form']['start_date']),"%Y-%m-%d").strftime("%d/%m/%Y")
        end_date = datetime.strptime(str(data['form']['end_date']),"%Y-%m-%d").strftime("%d/%m/%Y")
        docargs = {
            'doc_ids': data.get('ids', data.get('active_ids')),
            'data':{
                    'start_date' : start_date,
                    'end_date' : end_date,   
                    'data_list': data['dataline'] or [],
                    'total' : data['total'] or []              
                    }
            }
        return self.env['report'].render('product_sale.report_product_sale_template', docargs)