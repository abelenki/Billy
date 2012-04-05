#!/usr/bin/python
# -*- coding: utf-8 -*-

import unittest

from common.models import *
from test.support_random import *

from datetime import datetime
from datetime import timedelta


class TestModelGenerator(unittest.TestCase):

    def setUp(self):
        self.account = random_account()
        self.customer = random_customer(self.account)
        self.company = random_company()

    def test_invoice_put(self):
        invoice = Invoice(company=self.company)
        invoice.customer = self.customer


            # invoice.description =
            #
            # if key:
            #    if self.request.get('is_payed'):
            #        log.text = 'save: marked invoice payed'
            #        invoice.is_payed = True
            #        invoice.payed = datetime.now()
            #    else:
            #        log.text = 'save: unmarked invoice payed'
            #        invoice.payed = None  # datetime.now()
            #        invoice.is_payed = False
            #
            #    if self.request.get('payed'):
            #        invoice.payed = datetime.strptime(self.request.get('payed'),
            #                '%Y-%m-%d')
            #
            #    if self.request.get('is_billed'):
            #        invoice.billed = datetime.now()
            #        invoice.is_billed = True
            #    else:
            #        invoice.is_billed = False
            #        invoice.billed = None
            #
            #    if self.request.get('billed'):
            #        invoice.billed = datetime.strptime(self.request.get('billed'
            #                ), '%Y-%m-%d')
            #        log.text = 'save: set invoice to billed %s' \
            #            % invoice.billed.date()
            #
            # invoice.put()
            # log.invoice = invoice
            # log.put()
            # self.redirect('/invoice/edit/%s' % invoice.key())
            #
            #
        # gen = Generator.get(self.get_random_generator().key())
        #
        # self.assertEqual(gen.unit, 'days', 'is a generator')
        # self.assertEqual(gen.description, 'foo', 'is a generator')
        # self.assertTrue(isinstance(gen, Generator))
        # self.assertTrue(isinstance(gen.account, Account))
        # self.assertTrue(isinstance(gen.customer, Customer))
