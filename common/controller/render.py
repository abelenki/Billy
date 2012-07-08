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

    def mailAction(self, key):
    
        # template_values = {}
    
        account = Account().current()
    
        if account.send_mail == False:  # TODO find a better mechanism to limit e-mail
            output = StringIO.StringIO()
            invoice = Invoice.get(urllib.unquote(key))
            self._check_account(invoice.account)
            customer = invoice.customer
    
            invoice = Invoice.get(urllib.unquote(key))
            invoice_render = render.Invoice(invoice, output)
    
            filename = '%s_%s-%s.pdf' % (invoice.customer.firstname.replace(' ',
                                         '_'),
                                         invoice.customer.surname.replace(' ', '_'
                                         ), invoice.billing_number())
    
            invoice_render.save()
    
            mail.send_mail(sender=invoice.company.email, to='%s <%s>'
                           % (customer.fullname(), customer.email),
                           subject=invoice.description,
                           body=invoice.billing_introduction(),
                           attachments=[(filename, output.getvalue())])
    
            log = InvoiceLog()
            log.text = 'mail: send invoice per mail to %s' % invoice.company.email
            log.invoice = invoice
            log.put()
    
        self.redirect(self.request.get('continue', '/'))
    
    def invoiceAction(self, key):
        temlate_values = {}
    
        invoice = Invoice.get(urllib.unquote(key))
        self._check_account(invoice.account)
    
        invoice_render = render.Invoice(invoice, self.response.out)
    
        filename = '%s_%s-%s.pdf' % (invoice.customer.firstname.replace(' ', '_'
                                     ), invoice.customer.surname.replace(' ', '_'
                                     ), invoice.billing_number())
    
        self.response.headers['Content-Type'] = 'application/pdf'
        self.response.headers['Content-Disposition'] = 'attachment; filename=%s' \
            % filename
    
        invoice_render.save()
