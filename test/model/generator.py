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
        unit='day',
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

    def test_generator_put(self):
        gen = Generator.get(self.get_random_generator().key())

        self.assertEqual(gen.unit, 'day', 'is a generator')
        self.assertEqual(gen.description, 'foo', 'is a generator')
        self.assertTrue(isinstance(gen, Generator))
        self.assertTrue(isinstance(gen.account, Account))
        self.assertTrue(isinstance(gen.customer, Customer))

    def test_generator_run(self):
        date_start = datetime.today() - timedelta(days=10)
        gen = self.get_random_generator(start=date_start)
        gen.run()

        self.assertEqual(gen.count, 10)


