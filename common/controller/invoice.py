#!/usr/bin/python
# -*- coding: utf-8 -*-

from __init__ import *

from common.models import *
from common.pager import Pager
from common import render

from base import BaseController
import logging


class Controller(BaseController):

    template_module = 'invoice'

    def get(self, action, key=None):
        account = Account().current()

        if action.rstrip('/') == 'render':
            self.renderAction(key)
            return

        if action.rstrip('/') == 'mail':
            self.mailAction(key)
            return

        if not account.companies():
            self.template_values['notice'] = \
                """
                <a id="context-add" class="button" href="/company/edit/">add company</a>
                <h4><strong>You did not create a company yet!</strong></h4>
                <p>You should really go and create a company <em><a href='/company/edit/'>now</a></em> ;-)</p>
            """
        elif not account.customers():
            self.template_values['notice'] = \
                """
                <a id="context-add" class="button" href="/customer/edit/">add customer</a>
                <h4><strong>No customers found!</strong></h4>
                <p>We strongly suggest you get one <strong><a href='/customer/edit/'>now</a></strong> ;-)</p>
            """

        return super(Controller, self).get(action, key)

    def saveAction(self, key):
        if self.request.method == 'POST':
            log = InvoiceLog()

            if not key:
                company = db.get(self.request.get('company'))
                self._check_account(company.account)

                invoice = Invoice(company=company)

                log.text = "save: created new invoice '%s'" \
                    % self.request.get('description').replace('\n', ' ')
            else:
                invoice = Invoice.get(key)
                self._check_account(invoice.account)
                log.text = "save: saved '%s'" % invoice.description

            invoice.customer = db.get(self.request.get('customer'))
            invoice.description = self.request.get('description').replace('\n', ''
                    ).strip()

            if key:
                if self.request.get('is_payed'):
                    log.text = 'save: marked invoice payed'
                    invoice.is_payed = True
                    invoice.payed = datetime.now()
                else:
                    log.text = 'save: unmarked invoice payed'
                    invoice.payed = None  # datetime.now()
                    invoice.is_payed = False

                if self.request.get('payed'):
                    invoice.payed = datetime.strptime(self.request.get('payed'),
                            '%Y-%m-%d')

                if self.request.get('is_billed'):
                    invoice.billed = datetime.now()
                    invoice.is_billed = True
                else:
                    invoice.is_billed = False
                    invoice.billed = None

                if self.request.get('billed'):
                    invoice.billed = datetime.strptime(self.request.get('billed'
                            ), '%Y-%m-%d')
                    log.text = 'save: set invoice to billed %s' \
                        % invoice.billed.date()

            invoice.put()
            log.invoice = invoice
            log.put()
            self.redirect('/invoice/edit/%s' % invoice.key())

    def addlineAction(self, key):
        invoice = Invoice.get(key)
        self._check_account(invoice.account)

        try:

            InvoiceLine(invoice=invoice, name=self.request.get('name'),
                        amount=float(self.request.get('amount'))).put()

            self.redirect('/invoice/edit/%s' % key)
        except ValueError, error:
            self.redirect('/invoice/edit/%s?error=%s' % (key, error))

    def savelineAction(self, key):
        line = InvoiceLine.get(key)

        self._check_account(line.invoice.account)

        line.name = self.request.get('name')
        line.amount = float(self.request.get('amount'))

        line.put()

        self.redirect('/invoice/edit/%s' % line.invoice.key())

    def dellineAction(self, key):
        line = InvoiceLine.get(key)

        self._check_account(line.invoice.account)

        invoice = line.invoice
        line.delete()

        self.redirect('/invoice/edit/%s' % invoice.key())

    def viewAction(self, key):
        invoice = db.get(key)

        self._check_account(invoice.account)

        self.template_values['invoice'] = invoice
        self.template_values['customers'] = invoice.account.customers()
        self.template_values['invoices'] = invoice.invoices(0, 10)

    def listAction(self, invoice_key):
        account = Account().current()

        gql = []

        tab = self.request.get('tab')
        if tab == 'all':
            invoices = Invoice.gql('where account = :1 order by billed asc',
                                   account.key())
        elif tab == 'billed':
            invoices = \
                Invoice.gql('where account = :1 and is_billed = true and is_payed = false order by billed asc'
                            , account.key())
        elif tab == 'payed':
            invoices = \
                Invoice.gql('where payed > 0 and account = :1 order by payed asc'
                            , account.key())
        elif tab == 'billable':
            invoices = \
                Invoice.gql('where account = :1 and is_billed = False order by created'
                            , account.key())
        else:
            tab = 'overdue'
            invoices = \
                Invoice.gql('\
                where account = :1 \
                and is_billed = True\
                and is_payed = False\
                and billed < :2\
                order by billed asc'
                            , account.key(), datetime.now() - timedelta(16))

        pager = Pager(invoices, self.request.get('page'), self.request.get('first'
                      ))

        self.template_values['invoices'] = pager.fetch(35)
        self.template_values['request'] = self.request
        self.template_values['pager'] = pager
        self.template_values['tab'] = tab

    def deleteAction(self, key):
        invoice = Invoice.get(urllib.unquote(key))
        self._check_account(invoice.account)

        for line in invoice.invoice_lines():
            line.delete()

        invoice.delete()
        self.redirect('/invoice/list/')

    def editAction(self, key):
        account = Account().current()

        self.template_values['customers'] = account.customers()
        self.template_values['companies'] = account.companies()

        if key:
            invoice = Invoice.get(key)
            self._check_account(invoice.account)

            total = sum(line.amount for line in invoice.invoice_lines())
            self.template_values['invoice_total'] = total
            self.template_values['key'] = key

            if invoice.customer:
                self.template_values['customer_key'] = invoice.customer.key()

            if invoice.is_payed:
                self.template_values['payed'] = invoice.payed.strftime('%Y-%m-%d')

            if invoice.billed:
                self.template_values['billed'] = \
                    invoice.billed.strftime('%Y-%m-%d')
        else:
            invoice = Invoice()

            if self.request.get('customer'):
                self.template_values['customer_key'] = self.request.get('customer'
                        )

        self.template_values['invoice'] = invoice

