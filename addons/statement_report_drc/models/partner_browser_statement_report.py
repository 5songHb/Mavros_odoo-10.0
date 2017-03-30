# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError
import datetime
from dateutil.relativedelta import relativedelta


class CustomerAccountStatement(models.TransientModel):
    _name = "account.statement.wizard.customer"


    @api.model
    def _get_partner_ids(self):
        if self.env.context:
            partners = []
            partners = self.env.context.get('active_ids', [])
        return partners

    new_radio = fields.Selection([('cust', 'Customer'), ('supp', 'Supplier'), ('cust&supp', 'Customer & Supplier')], default='cust', string="Selection")
    partner_id = fields.Many2many('res.partner', 'name', string='Partner', required=True, default=_get_partner_ids)
    date_from = fields.Date(string="Start Date")
    date_to = fields.Date(string="End Date")
    posted = fields.Selection([('draft', 'All Entries'), ('posted', 'Posted Entries')], default='draft')
    currency_id = fields.Selection([('base', 'Company Currency'), ('foreign', 'Partner Currency')], default='base', string="Currency")

    @api.multi
    @api.onchange('currency_id')
    def onchange_currency_id(self):
        if self.currency_id == "foreign":
            if not self.partner_id:
                raise UserError(_("Please select partner."))
            for i in self.partner_id:
                if i.supplier and not i.property_purchase_currency_id:
                    raise UserError(_("please configure supplier currency in vendor : " + i.name))

    @api.multi
    def print_report(self):
        # self.ensure_one()
        data = {}
        data['ids'] = self.env.context.get('active_ids', [])
        data['model'] = self.env.context.get('active_model', 'ir.ui.menu')
        data['form'] = self.read(['date_from', 'date_to'])[0]
        data['form']['partner_id'] = self.partner_id.ids
        data['form']['posted'] = str(self.posted)
        data['form']['new_radio'] = str(self.new_radio)
        data['form']['currency'] = str(self.currency_id)
        return self.env['report'].get_action(self, 'statement_report_drc.account_statement_report_customer', data=data)


class PartnerAccountStatementReport(models.Model):
    _name = 'report.statement_report_drc.account_statement_report_customer'

    def _get_account_move_entry(self, accounts, sortby, display_account, partner_id, posted, account_type, currency_id, date_from, date_to):
        cr = self.env.cr
        MoveLine = self.env['account.move.line']
        move_lines = dict(map(lambda x: (x, []), accounts.ids))
        x_move_lines = {}
        sql_sort = 'l.date, l.move_id'

        # Prepare sql query base on selected parameters from wizard
        tables, where_clause, where_params = MoveLine._query_get()
        wheres = [" "]
        if partner_id:
            wheres += ["l.partner_id = %s" % tuple(partner_id)]
        if where_clause.strip():
            wheres.append(where_clause.strip())

        filters = " AND ".join(wheres)
        filters = filters.replace('account_move_line__move_id', 'm').replace('account_move_line', 'l')

        opening = 0.0
        real_opening = 0.0
        sql = """SELECT l.id AS lid, l.account_id AS account_id, l.date AS ldate, j.code AS lcode, l.currency_id, l.amount_currency, l.ref AS lref, l.name AS lname, COALESCE(l.debit,0) AS debit, COALESCE(l.credit,0) AS credit, COALESCE(SUM(l.debit),0) - COALESCE(SUM(l.credit), 0) AS balance,\
            m.name AS move_name, c.symbol AS currency_code, p.name AS partner_name\
            FROM account_move_line l\
            JOIN account_move m ON (l.move_id=m.id)\
            LEFT JOIN res_currency c ON (l.currency_id=c.id)\
            LEFT JOIN res_partner p ON (l.partner_id=p.id)\
            JOIN account_journal j ON (l.journal_id=j.id)\
            JOIN account_account acc ON (l.account_id = acc.id)\
            WHERE l.account_id IN %s AND m.state IN ('""" + "','".join(posted)
        sql += "') "
        if date_from:
            sql += " AND l.date < '" + str(date_from) + "' "
        else:
            date_from = datetime.datetime.strftime(datetime.datetime.today(), "%Y-%m-%d")
            date_from = datetime.datetime.strptime(date_from, "%Y-%m-%d")
            date_from = date_from.replace(month=1, day=1, year=date_from.year)
            date_from = datetime.datetime.strftime(date_from, "%Y-%m-%d")
            sql += " AND l.date < '" + str(date_from) + "' "
        sql += " AND (acc.internal_type IN %s) "
        sql += filters + ' GROUP BY l.id, l.account_id, l.date, j.code, l.currency_id, l.amount_currency, l.ref, l.name, m.name, c.symbol, p.name ORDER BY ' + sql_sort
        params = (tuple(accounts.ids),) + tuple(where_params) + (tuple(account_type),)
        cr.execute(sql, params)
        if sortby == 'sort_date':
            for index, row in enumerate(cr.dictfetchall()):
                if currency_id and row['amount_currency']:
                    opening += row['amount_currency']
                if not row['currency_id']:
                    opening += row['balance']
            real_opening = opening

        # Get move lines base on sql query and Calculate the total balance of move lines
        sql = """SELECT l.id AS lid, l.account_id AS account_id, l.date AS ldate, j.code AS lcode, l.currency_id, l.amount_currency, l.ref AS lref, l.name AS lname, COALESCE(l.debit,0) AS debit, COALESCE(l.credit,0) AS credit, COALESCE(SUM(l.debit),0) - COALESCE(SUM(l.credit), 0) AS balance,\
            m.name AS move_name, c.symbol AS currency_code, p.name AS partner_name\
            FROM account_move_line l\
            JOIN account_move m ON (l.move_id=m.id)\
            LEFT JOIN res_currency c ON (l.currency_id=c.id)\
            LEFT JOIN res_partner p ON (l.partner_id=p.id)\
            JOIN account_journal j ON (l.journal_id=j.id)\
            JOIN account_account acc ON (l.account_id = acc.id)\
            WHERE l.account_id IN %s AND m.state IN ('""" + "','".join(posted)
        sql += "') "
        if date_from:
            sql += " AND l.date >= '" + str(date_from) + "' "
        if date_to:
            sql += " AND l.date <= '" + str(date_to) + "' "
        sql += " AND (acc.internal_type IN %s) "
        sql += filters + ' GROUP BY l.id, l.account_id, l.date, j.code, l.currency_id, l.amount_currency, l.ref, l.name, m.name, c.symbol, p.name ORDER BY ' + sql_sort
        params = (tuple(accounts.ids),) + tuple(where_params) + (tuple(account_type),)
        cr.execute(sql, params)

        if sortby == 'sort_date':
            for index, row in enumerate(cr.dictfetchall()):
                balance = 0
                for line in x_move_lines.get(index, []):
                    balance += line['debit'] - line['credit']
                row['balance'] += balance
                x_move_lines[index] = [row]
        # Calculate the debit, credit and balance for Accounts
        side_balance = 0
        account_res = []
        if sortby == 'sort_date':
            for key, value in x_move_lines.items():
                res = dict((fn, 0.0) for fn in ['credit', 'debit', 'balance'])

                if value[0]['debit'] != 0 or value[0]['credit'] != 0:
                    res['move_lines'] = value
                    for line in res.get('move_lines'):
                        currency_rate = 1
                        if currency_id != line['currency_id']:
                            if not line['currency_id']:
                                currency1 = self.env['res.currency'].search([('id', '=', self.env.user.company_id.currency_id.id)]).rate
                            else:
                                currency1 = self.env['res.currency'].search([('id', '=', line['currency_id'])]).rate
                            currency2 = self.env['res.currency'].search([('id', '=', currency_id)]).rate
                            currency_rate = round(currency2 / currency1, 2)
                            side_balance += opening
                            if line['debit']:
                                if line['amount_currency']:
                                    amount = round(abs(currency_rate * line['amount_currency']), 2)
                                    res['debit'] += amount
                                    side_balance += amount
                                else:
                                    res['debit'] += round(abs(line['debit']), 2)
                                    side_balance += round(abs(line['debit']), 2)
                            else:
                                res['debit'] += round(abs(line['debit']), 2)
                                side_balance += round(abs(line['debit']), 2)
                            if line['credit']:
                                if line['amount_currency']:
                                    amount = round(abs(currency_rate * line['amount_currency']), 2)
                                    res['credit'] += amount
                                    side_balance -= amount
                                else:
                                    res['credit'] += round(abs(line['credit']), 2)
                                    side_balance -= round(abs(line['credit']), 2)
                            else:
                                res['credit'] += round(abs(line['credit']), 2)
                                side_balance -= round(abs(line['credit']), 2)
                            opening = 0
                            res['balance'] = round(side_balance, 2)
                        else:
                            res['debit'] += round(abs(line['debit']), 2)
                            res['credit'] += round(abs(line['credit']), 2)
                            side_balance += round(opening + abs(line['debit']) - abs(line['credit']), 2)
                            opening = 0
                            res['balance'] = side_balance

                    if display_account == 'all':
                        account_res.append(res)

        return account_res, real_opening

    def _get_partner_move_lines(self, account_type, partner, date_from, date_to, target_move, period_length, opening):
        periods = {}
        if not date_from:
            date_from = datetime.datetime.strftime(datetime.datetime.today(), "%Y-%m-%d")
            account_payment = self.env['account.payment'].search([('partner_id', '=', partner.id)])
        else:
            account_payment = self.env['account.payment'].search([('partner_id', '=', partner.id),('payment_date','>=',date_from)])
        start = datetime.datetime.strptime(date_from, "%Y-%m-%d")
        for i in range(5)[::-1]:
            if i == 4:
                if start.month == 12:
                    stop = start.replace(month=1, day=1, year=start.year+1) - relativedelta(days=1)
                else:
                    stop = start.replace(month=start.month+1, day=1) - relativedelta(days=1)
                start = start.replace(month=1, day=1, year=start.year)
                periods[str(i)] = {
                    'name': start.strftime('%m'),
                    'stop': stop.strftime('%Y-%m-%d'),
                    'start': start.strftime('%Y-%m-%d'),
                }
            elif i == 0:
                if start.month == 12:
                    stop = start.replace(month=1, day=1, year=start.year+1) - relativedelta(days=1)
                else:
                    stop = start.replace(month=1, day=1, year=start.year+1) - relativedelta(days=1)
                periods[str(i)] = {
                    'name': start.strftime('%m'),
                    'stop': stop.strftime('%Y-%m-%d'),
                    'start': (i!=4 and start.strftime('%Y-%m-%d') or False),
                }
            else:
                if start.month == 12:
                    stop = start.replace(month=1, day=1, year=start.year+1) - relativedelta(days=1)
                else:
                    stop = start.replace(month=start.month+1, day=1) - relativedelta(days=1)
                periods[str(i)] = {
                    'name': start.strftime('%m'),
                    'start': start.strftime('%Y-%m-%d'),
                    'stop': (i!=4 and stop.strftime('%Y-%m-%d') or False),
                }
            start = stop + relativedelta(days=1)

        res = {}
        final_list = []
        if not date_to:
            account_invoice = self.env['account.invoice'].search([('partner_id', '=', partner.id), ('state', '=', 'open')])
        else:
            account_invoice = self.env['account.invoice'].search([('partner_id', '=', partner.id), ('state', '=', 'open'), ('date_invoice','<=',date_to)])
        for i in periods:
            dict1 = {}
            list1 = []
            for ac in account_invoice:
                if ac.date_due:
                    if periods[i]['start']:
                        if datetime.datetime.strptime(ac.date_due, "%Y-%m-%d") >= datetime.datetime.strptime(periods[i]['start'], "%Y-%m-%d") and datetime.datetime.strptime(ac.date_due, "%Y-%m-%d") <= datetime.datetime.strptime(periods[i]['stop'], "%Y-%m-%d"):
                            list1.append(ac)
                    else:
                        if datetime.datetime.strptime(ac.date_due, "%Y-%m-%d") <= datetime.datetime.strptime(periods[i]['stop'], "%Y-%m-%d"):
                            list1.append(ac)
            dict1.update({i: list1})
            final_list.append(dict1)
        total = 0
        for fl in final_list:
            for f in fl:
                if f == '4':
                    total = opening
                    for tot in fl[f]:
                        total += tot.residual_signed
                    for new in account_payment:
                        total -= new.amount
                else:
                    total = 0
                    for tot in fl[f]:
                        total += tot.residual_signed
                res.update({f: total})
        res.update({'partner_id': partner.id, 'name': partner.name})
        return res


    @api.multi
    def render_html(self, docids, data=None):
        self.model = self.env.context.get('active_model')
        docs = self.env[self.model].browse(self.env.context.get('active_id'))

        sortby = 'sort_date'
        display_account = 'all'
        partner_id = data['form']['partner_id']
        posted = ['draft', 'posted']
        if data['form']['posted'] and data['form']['posted'] == "posted":
            posted = ['posted']
        partners = self.env['res.partner'].search([('id', 'in', partner_id)])
        final_res = []
        final_res2 = []

        for partner in partners:
            accounts_res = []
            final_dict = {}
            if data['form']['new_radio'] == 'cust':
                account_type = ['receivable']
            elif data['form']['new_radio'] == 'supp':
                account_type = ['payable']
            elif data['form']['new_radio'] == 'cust&supp':
                account_type = ['payable', 'receivable']
            if self.env.user.company_id.currency_id and data['form']['currency'] == 'base':
                data['form']['currency_id'] = self.env.user.company_id.currency_id.id
            if self.env.user.company_id.currency_id and data['form']['currency'] == 'foreign' and partner and partner.supplier:
                data['form']['currency_id'] = partner.property_purchase_currency_id and partner.property_purchase_currency_id.id
            if self.env.user.company_id.currency_id and data['form']['currency'] == 'foreign' and partner and partner.customer:
                data['form']['currency_id'] = self.env.user.company_id.currency_id.id
            accounts = self.env['account.account'].search([('id', 'in', [partner.property_account_payable_id and partner.property_account_payable_id.id or False, partner.property_account_receivable_id and partner.property_account_receivable_id.id or False])])
            accounts_res, opening = self.with_context(data['form'].get('used_context',{}))._get_account_move_entry(accounts, sortby, display_account, [partner.id], posted, account_type, data['form']['currency_id'], data['form']['date_from'], data['form']['date_to'])
            final_dict.update({'lines': accounts_res, 'opening': opening, 'partner': partner, 'currency': self.env['res.currency'].search([('id', '=', data['form']['currency_id'])]).name})
            final_res.append(final_dict)

            movelines = self._get_partner_move_lines(account_type, partner, data['form']['date_from'],data['form']['date_to'], posted, 30, opening)
            final_res2.append(movelines)

        docargs = {
            'doc_ids': self.ids,
            'doc_model': self.model,
            'data': data['form'],
            'docs': final_res,
            'get_partner_lines': final_res2,
            'Accounts': accounts_res,
        }
        return self.env['report'].render('statement_report_drc.account_statement_report_customer', docargs)















































    # @api.multi
    # def render_html(self, docids, data=None):
        # self.model = self.env.context.get('active_model')
        # print "<<<<<<<<<<>>>>>>>>>>>>",self.env.context
        # docs = self.env['res.patner'].browse(self.env.context.get('active_id'))
        # print "***********************",docs

        # sortby = 'sort_date'
        # display_account = 'all'
        # partner_id = docids
        # posted = ['posted']
        # partners = self.env['res.partner'].search([('id', 'in', partner_id)])
        # currency_id = self.env.user.company_id.currency_id.id
        # account_type = ['receivable']   
        # date_from = datetime.datetime.strftime(datetime.datetime.today(), "%Y-%m-%d")
        # date_from = datetime.datetime.strptime(date_from, "%Y-%m-%d")
        # date_from = date_from.replace(month=1, day=1, year=date_from.year)
        # date_from = datetime.datetime.strftime(date_from, "%Y-%m-%d")
        # date_to = False
        # final_res = []
        # final_res2 = []

        # for partner in partners:
        #     accounts_res = []
        #     final_dict = {}
            # if data['form']['new_radio'] == 'cust':
            #     account_type = ['receivable']
            # elif data['form']['new_radio'] == 'supp':
            #     account_type = ['payable']
            # elif data['form']['new_radio'] == 'cust&supp':
            #     account_type = ['payable', 'receivable']
            # if self.env.user.company_id.currency_id and data['form']['currency'] == 'base':
            #     data['form']['currency_id'] = self.env.user.company_id.currency_id.id
            # if self.env.user.company_id.currency_id and data['form']['currency'] == 'foreign' and partner and partner.supplier:
            #     data['form']['currency_id'] = partner.property_purchase_currency_id and partner.property_purchase_currency_id.id
            # if self.env.user.company_id.currency_id and data['form']['currency'] == 'foreign' and partner and partner.customer:
            #     data['form']['currency_id'] = self.env.user.company_id.currency_id.id
        #     accounts = self.env['account.account'].search([('id', 'in', [partner.property_account_payable_id and partner.property_account_payable_id.id or False, partner.property_account_receivable_id and partner.property_account_receivable_id.id or False])])
        #     accounts_res, opening = self._get_account_move_entry(accounts, sortby, display_account, [partner.id], posted, account_type, currency_id, date_from, date_to)
        #     final_dict.update({'lines': accounts_res, 'opening': opening, 'partner': partner, 'currency': self.env['res.currency'].search([('id', '=', currency_id)]).name})
        #     final_res.append(final_dict)

        #     movelines = self._get_partner_move_lines(account_type, partner,date_from,date_to, posted, 30, opening)
        #     final_res2.append(movelines)

        # docargs = {
        #     'doc_ids': self.ids,
        #     'doc_model': 'res.partner',
        #     # 'data': data['form'],
        #     'docs': final_res,
        #     'get_partner_lines': final_res2,
        #     'Accounts': accounts_res,
        # }
        # return self.env['report'].render('statement_report_drc.account_statement_report_customer', docargs)
