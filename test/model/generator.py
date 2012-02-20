#!/usr/bin/python
# -*- coding: utf-8 -*-

import unittest

from common.models import *
from test.support_random import *

from datetime import datetime
from datetime import timedelta

# from dateutil.relativedelta import relativedelta


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
        start=datetime.now(),
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

        date_start = datetime.today() \
            - relativedelta(months=settings['months'],
                            weeks=settings['weeks'],
                            days=settings['days'])

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

        intervals = {'days': (10, 3, 3), 'weeks': (7, 2, 3),
                     'months': (10, 3, 3)}

        for unit in iter(intervals):
            (offset, interval, expected_count) = intervals[unit]
            settings = default.copy()
            settings[unit] = offset

            gen = self.run_generator(unit, interval, settings)

            self.assertEqual(gen.count, expected_count,
                'run counter is %d' % expected_count)

            invoices = GeneratorInvoice.gql('WHERE generator = :1', gen.key())
            self.assertEqual(invoices.count(), expected_count,
                'exactly %d invoices' % expected_count)

