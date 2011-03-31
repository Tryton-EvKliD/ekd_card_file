# -*- coding: utf-8 -*-
"Card File"
from trytond.model import ModelView, ModelSQL, fields
from trytond.wizard import Wizard
from trytond.transaction import Transaction
from trytond.tools import safe_eval
from decimal import Decimal, ROUND_HALF_EVEN
from trytond.pyson import In, Eval, Not, In, Equal, If, Get, Bool
import time
import datetime
import random
import copy

class CardTemplate(ModelSQL, ModelView):
    "Card Template"
    _name='ekd.card_file.template'
    _description=__doc__

    company = fields.Many2One('company.company', 'Company', readonly=True)
    model = fields.Many2One('ir.model', 'Model', domain=[('model','like','ekd.card_file.head%')])
    model_str = fields.Char('Model Name', size=128)
    name = fields.Char('Name', size=128)
    shortcut = fields.Char('ShortCut', size=32)
    code_call = fields.Char('Code Call', size=20, help="income, expense, ...")
    sort = fields.Char('Sort', size=4)
    type_card = fields.Selection('type_account_get', 'Type account')
    sequence = fields.Many2One('ir.sequence', 'Sequence')
    view_form  = fields.Many2One('ir.action.act_window', 'Form View', 
                    domain=[('res_model','like','ekd.document.%')])
    report = fields.Many2One('ir.action.report', 'Form for print')
    date_start = fields.Date('Date Start')
    date_end = fields.Date('Date end')
    active = fields.Boolean('Active')

    def default_company(self):
        return Transaction().context.get('company') or False

    def default_active(self):
        return True

    def type_account_get(self):
        dictions_obj = self.pool.get('ir.dictions')
        res = []
        diction_ids = dictions_obj.search([
                ('model', '=', 'ekd.card_file.template'),
                ('pole', '=', 'type_card'),
                ])
        for diction in dictions_obj.browse(diction_ids):
            res.append([diction.key, diction.value])
        return res


CardTemplate()

class CardFile(ModelSQL, ModelView):
    "Card"
    _name='ekd.card_file.card'
    _order_name = 'date_card'
    _description=__doc__

    company = fields.Many2One('company.company', 'Company', readonly=True)
    model = fields.Many2One('ir.model', 'Model', domain=[('model','like','ekd.document%')])
    model_str = fields.Char('Model Name', size=128)
    name = fields.Char('Description')
    template = fields.Many2One('ekd.card_file.template', 'Crad Name', help="Template card", order_field="%(table)s.template %(order)s")
    note = fields.Text('Note Card')
    number = fields.Char('Number', size=32, readonly=True)
    date_card = fields.Date('Date Create')
    date_account = fields.Date('Date Account')
    employee = fields.Many2One('company.employee', 'Employee')
    party = fields.Many2One('party.party', 'Party')
    amount = fields.Numeric('Amount', digits=(16, Eval("currency_digits",2)))
    currency = fields.Many2One('currency.currency', 'Currency')
    currency_digits = fields.Function(fields.Integer('Currency Digits' , on_change_with=['currency']), 'get_currency_digits')
    document_base = fields.Reference('Document Base', selection='documents_base_get',
                on_change=['document_base', 'lines'])
    lines = fields.One2Many('ekd.document.line.product', 'invoice', 'Lines')
    parent = fields.One2Many('ekd.document','child', 'Parent Card')
    child = fields.Many2One('ekd.document', 'Child Card')
    state = fields.Char('State', size=None, translate=True, readonly=True)
    post_date = fields.Date('Date Post')
    active = fields.Boolean('Active', required=True)   
    id_1c = fields.Char("ID import from 1C", size=None, select=1)
    deleting = fields.Boolean('Flag Deleting')

    def __init__(self): 
        super(CardFile, self).__init__()

        self._order.insert(0, ('company','ASC')) 
        self._order.insert(0, ('date_card', 'ASC')) 
        self._order.insert(0, ('template', 'ASC')) 
        self._order.insert(0, ('date_account', 'ASC')) 
        self._order.insert(0, ('number', 'ASC')) 

    def default_state(self):
        return 'draft'

    def default_date_card(self):
        context = Transaction().context
        if context.get('date_card'):
            return context.get('date_card')
        elif context.get('current_date'):
            return context.get('current_date')
        return datetime.datetime.now()

    def default_date_account(self ):
        context = Transaction().context
        if context.get('date_account'):
            return context.get('date_account')
        elif context.get('current_date'):
            return context.get('current_date')
        return datetime.datetime.now()

    def default_party(self):
        context = Transaction().context
        if context.get('party'):
            return context.get('party')
        return

    def default_company(self ):
        return Transaction().context.get('company') or False

    def default_child(self):
        context = Transaction().context
        if context.get('child'):
            return context.get('child')
        return

    def default_amount(self):
        context = Transaction().context
        if context.get('amount'):
            return context.get('amount')
        return

    def default_name(self):
        context = Transaction().context
        if context.get('name'):
            return context.get('name')
        return

    def default_note(self):
        context = Transaction().context
        if context.get('note'):
            return context.get('note')
        return

    def default_currency(self):
        company_obj = self.pool.get('company.company')
        currency_obj = self.pool.get('currency.currency')
        context = Transaction().context
        if context.get('company'):
            company = company_obj.browse(context['company'])
            return company.currency.id
        return False

    def default_currency_digits(self):
        company_obj = self.pool.get('company.company')
        context = Transaction().context
        if context.get('company'):
            company = company_obj.browse(context['company'])
            return company.currency.digits
        return 2

    def default_active(self):
        return True

    def documents_base_dict_get(self, model=False):
        if not model:
            model = self._name
        dictions_obj = self.pool.get('ir.dictions')
        res = []
        diction_ids = dictions_obj.search( [
                                ('model', 'like', 'ekd.card_file.head%'),
                                ('pole', '=', 'document_base'),
                                ])
        if diction_ids:
            for diction in dictions_obj.browse( diction_ids):
                res.append([diction.key, diction.value])
        return res

    def documents_base_get(self):
        return self.documents_base_dict_get(self._name)

    def get_currency_digits(self, ids, name):
        assert name in ('currency_digits'), 'Invalid name %s' % (name)
        res={}.fromkeys(ids, 2)
        for document in self.browse(ids):
            if document.currency:
                res[document.id] = document.currency.digits
        return res

    def button_draft(self, ids):
        for document in self.browse(ids):
            if document.template.model:
                self.pool.get(document.template.model).button_draft(ids)

    def button_cancel(self, ids):
        for document in self.browse(ids):
            if document.template.model:
                self.pool.get(document.template.model).button_cancel(ids)

    def button_restore(self, ids):
        for document in self.browse(ids):
            if document.template.model:
                self.pool.get(document.template.model).button_restore(ids)

    def button_post(self, ids):
        for document in self.browse(ids):
            if document.template.model:
                self.pool.get(document.template.model).button_issued(ids)

    def button_confirmed(self, ids):
        for document in self.browse(ids):
            if document.template.model:
                self.pool.get(document.template.model).button_confirmed(ids)

CardFile()

class CardTemplate(ModelSQL, ModelView):
    "Card File Template"
    _name='ekd.card_file.template'

    cards = fields.One2Many('ekd.card_file','template','Real Documents')

CardTemplate()

class CardOpenWizard(Wizard):
    'Open Card Wizard'
    _name = 'ekd.card_file.wizard.open'
    states = {
        'init': {
            'result': {
                'type': 'action',
                'action': '_add',
                'state': 'end'
                        },
                },
            }

    def _add(self, data):
        document_obj = self.pool.get('ekd.card_file')
        model_obj = self.pool.get('ir.model')
        model_data_obj = self.pool.get('ir.model.data')
        act_window_obj = self.pool.get('ir.action.act_window')

        document = document_obj.browse(data.get('id'))
        if document.template.view_form:
            res = act_window_obj.read(document.template.view_form.id)
            res['res_id'] = data.get('id')
            res['views'].reverse()
            return res
        else:
            self.raise_user_error('Form View not find!\nPlease setup template document:\n\n %s'%(document.template.name))

CardOpenWizard()
