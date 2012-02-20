#!/usr/bin/python
# -*- coding: utf-8 -*-

import unittest

from common.models import *
from test.support_random import *

from datetime import datetime
from datetime import timedelta

class TestModelGenerator(unittest.TestCase):

    """
    smoke testing the billy invoice generator
    """

    def setUp(self):

        self.account = random_account()
        self.customer = random_customer(self.account)
        self.company = random_company()

        pass

    def get_random_generator(
        self,
        interval=1,
        unit='days',
        start=datetime.today() - timedelta(days=3),
        ):

        generator = Generator()

        generator.account = self.account
        generator.company = self.company
        generator.customer = self.customer
        generator.start = start
        generator.description = 'foo'
        generator.interval = interval
        generator.unit = unit

        generator.put()
        return generator

    def run_generator(
        self,
        unit,
        interval,
        settings,
        ):

        date_start = datetime.today() - relativedelta(months=settings['months'],
                weeks=settings['weeks'], days=settings['days'])

        gen = self.get_random_generator(start=date_start, unit=unit,
                                        interval=interval)

        gen.run()
        return gen

    def test_generator_put(self):
        gen = Generator.get(self.get_random_generator().key())

        self.assertEqual(gen.unit, 'days', 'is a generator')
        self.assertEqual(gen.description, 'foo', 'is a generator')
        self.assertTrue(isinstance(gen, Generator))
        self.assertTrue(isinstance(gen.account, Account))
        self.assertTrue(isinstance(gen.customer, Customer))

    def test_generator_run(self):
        default = {'days': 0, 'weeks': 0, 'months': 0}
        intervals = {'days': (10, 3, 3), 'weeks': (7, 2, 3), 'months': (10, 3, 3)}

        for unit in iter(intervals):
            (offset, interval, expected_count) = intervals[unit]
            settings = default.copy()
            settings[unit] = offset

            gen = self.run_generator(unit, interval, settings)

            self.assertEqual(gen.count, expected_count, 'run counter is %d'
                             % expected_count)

            invoices = GeneratorInvoice.gql('WHERE generator = :1', gen.key())
            self.assertEqual(invoices.count(), expected_count,
                             'exactly %d invoices' % expected_count)

    def test_generator_invoice_lines_run(self):
        gen = self.get_random_generator()

        line_data = (('Line A', 21), ('Line B', 42), ('Line C', 84))

        for (name, amount) in line_data:
            line = GeneratorLine()
            line.generator = gen
            line.amount = float(amount)
            line.name = name

            line.put()

        lines = GeneratorLine.gql('WHERE generator = :1', gen.key())
        self.assertEqual(lines.count(), len(line_data), 'expected amount of lines'
                         )

        gen.run()
        generated_invoices = GeneratorInvoice.gql('WHERE generator = :1',
                gen.key()).fetch(100)

        for generated in generated_invoices:
            invoice_lines = generated.invoice.invoice_lines()
            self.assertEqual(invoice_lines.count(), len(line_data))

    def test_generator_invoice_lines_compare(self):
        gen = self.get_random_generator()
        line_data = (u'My line description with Fünny chars', 42)

        (description, amount) = line_data

        line = GeneratorLine(generator=gen, amount=float(amount),
                             name=description)
        line.put()

        generated_invoices = GeneratorInvoice.gql('WHERE generator = :1',
                gen.key()).fetch(100)

        for rel in generated_invoices:
            invoice_lines = rel.invoice.invoice_lines().fetch(100)

            self.assertEqual(len(invoice_lines), 1)
            self.assertEqual(invoice_lines[0].name, description)
            self.assertEqual(invoice_lines[0].amount, float(amount))
