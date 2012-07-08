#!/usr/bin/python
# -*- coding: utf-8 -*-

from __init__ import *
from common.models import *

from base import BaseController

import logging

from datetime import datetime


class Controller(BaseController):

    template_module = 'generator'

    def pre_dispatch(self, action, key=None):
        if key:
            self.generator = Generator.get(key)
            self._check_account(self.generator.account)
        else:
            self.generator = Generator()

    def run_action(self, key):
        self.generator.run()

    def save_action(self, key):
        for (key, prop) in Generator.properties().items():
            value = self.request.get(key)

            if not value:
                continue

            if type(prop).__name__ is 'IntegerProperty':
                value = int(value)

            if type(prop).__name__ is 'FloatProperty':
                value = float(value)

            if type(prop).__name__ is 'ReferenceProperty':
                value = db.get(value)

            if type(prop).__name__ is 'DateTimeProperty':
                value = datetime.strptime(value, '%Y-%m-%d')

            self.generator.__setattr__(key, value)

        if not self.generator.unit in ['days', 'weeks', 'months']:
            self.generator.unit = 'months'  # safeguard for invalid data

        self.generator.put()
        self.redirect('/generator/edit/%s' % self.generator.key())

    def edit_action(self, key):
        account = Account().current()

        self.template_values['customers'] = account.customers()
        self.template_values['companies'] = account.companies()
        self.template_values['last_run'] = 'never'

        if self.generator.lastrun:
            delta = datetime.today() - self.generator.lastrun
            self.template_values['last_run'] = '%d days ago' % delta.days

        self.template_values['generator'] = self.generator

    def delete_action(self, key):

        # lazy delete: should check if everything is cleaned up

        gen = Generator.get(key)

        lines = gen.lines().fetch(1000)
        db.delete(lines)

        logs = GeneratorLog.gql('WHERE generator = :1', gen.key())
        db.delete(logs.fetch(1000))

        refs = GeneratorInvoice.gql('WHERE generator = :1', gen.key())
        db.delete(refs.fetch(1000))

        gen.delete()

        self.redirect('/generator/list/')

    def list_action(self, key):
        account = Account().current()
        self.template_values['generators'] = account.generators()

    def addline_action(self, key):
        generator = Generator.get(urllib.unquote(key))
        line = GeneratorLine()

        line.generator = generator
        line.amount = float(self.request.get('amount'))
        line.name = self.request.get('name')

        line.put()

        self.redirect('/generator/edit/%s' % generator.key())

    def delline_action(self, key):
        line = GeneratorLine.get(urllib.unquote(key))

        generator = line.generator
        line.delete()

        self.redirect('/generator/edit/%s' % generator.key())


