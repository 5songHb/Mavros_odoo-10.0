# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, models
from datetime import datetime

class report_z(models.AbstractModel):
    
    _name = 'report.pos_z_report.report_pos_z'
    
    @api.model
    def render_html(self, docids, data=None):
        data = data if data is not None else {}
        date = datetime.strptime(str(data['form']['date']),"%Y-%m-%d").strftime("%d/%m/%Y")
        print "data['cashier_total']['total']",data['cashier_total']['total']
        docargs = {
            'doc_ids': data.get('ids', data.get('active_ids')),
            'data':{
                    'date' : date,
                    'location': data['form']['location_id'][1],
                    'total': data['cashier_total']['total'] or 0.0,
                    'cashier_total' : data['cashier_total']['cashier_total'] or []              
                    }
            }
        return self.env['report'].render('pos_z_report.report_pos_z', docargs)        
    