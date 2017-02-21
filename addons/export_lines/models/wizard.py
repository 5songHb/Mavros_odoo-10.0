# -*- coding: utf-8 -*-

from odoo import fields, models, api, _
from datetime import datetime
from odoo.exceptions import UserError
class SendMailWizard(models.TransientModel):
    _name = "send.mail.wizard"

    @api.multi
    def get_default_user(self):
        return self.env.user

    send_mail = fields.Boolean(string='Send email', default=False)
    email_cc_partner_ids = fields.Many2many('res.users', string="CC:", default=get_default_user)

    @api.multi
    def send_mail_to_logistic(self):
        active_ids = self._context.get('active_ids')
        active_model = self._context.get('active_model')
        records = self.env[active_model].browse(active_ids)
        for order in records:
            if active_model == 'sale.order':
                is_logistic = order.warehouse_id.is_logistic
                logistic_email = order.warehouse_id.partner_id.email
                filename = 'SO_'
                # route_name = 'SO'
            elif active_model == 'purchase.order':
                is_logistic = order.picking_type_id.warehouse_id.is_logistic
                logistic_email = order.picking_type_id.warehouse_id.partner_id.email
                filename = 'PO_'
                # route_name = 'PO'
            elif active_model == 'stock.picking':
                is_logistic = order.picking_type_id.warehouse_id.is_logistic
                logistic_email = order.picking_type_id.warehouse_id.partner_id.email
                filename = 'Transfer_'
                # route_name = 'PICK'
            if not is_logistic and self.send_mail:
                raise UserError(_("Unable to send email as the warehouse is not Logistic."))
            if self.send_mail:
                if not self.env.user.email:
                    raise UserError(_("Unable to send email, please configure your email address."))
                if not logistic_email:
                    raise UserError(_("Unable to send email, please configure Logistic partner's email address."))
                res = order.print_report_excel_data()
                data = res and res[0] or ''
                filename += str(datetime.now())
                values = {
                    'name': filename.lower() + '.xls',
                    'res_model': active_model,
                    'datas_fname': filename + '.xls',
                    'res_id': order.id,
                    'datas': data
                    }
                attachment = self.env['ir.attachment'].create(values)
                mail_mail = self.env['mail.mail']
                email_to = logistic_email
                subject = "Mavros New Orders"
                body = _("<span style='size:20px;font-family: Arial, Helvetica, sans-serif;'>The following Orders and/or  Invoices have been created: \n\n")
                body += filename + "\n\n" + "Mavros Ordering System" + '\n\n' + "DO NOT REPLY TO THIS EMAIL</span>"
                mail_params = {
                    'email_to': email_to,
                    'subject': subject,
                    'body_html': '<pre>%s</pre>' % body,
                    'attachment_ids': [(6, 0, [attachment.id])]
                    }
                cc_mail_string = ''
                for user in self.email_cc_partner_ids:
                    cc_mail_string += user.email + ','
                if self.email_cc_partner_ids:
                    mail_params['email_cc'] = cc_mail_string[0:len(cc_mail_string) - 1]
                mail_id = mail_mail.create(mail_params)
                mail_id.send()
                order.mail_sent = True
                order.mail_date_time = datetime.now()
        # uncomment this code if you also want to download excel file after sending mail to logisticss
        # Also uncomment the code for route_name variable above
        # return {
        #             "type": "ir.actions.act_url",
        #             'url': '/web/binary/download_document/%s/?obj=%s' % (route_name, self._context['active_ids']),
        #             'target': 'new'
        #             }
