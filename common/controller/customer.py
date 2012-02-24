#!/usr/bin/python
# -*- coding: utf-8 -*-
from __init__ import *
from common.models import *
from basecontroller import BaseController


class Controller(BaseController):

    template_module = 'customer'

    def get(self, action, key=None):
        if key:
            customer = Customer.get(key)
            self._check_account(customer.account)

        super(Controller, self).get(action, key)

    def post(self, action, key=None):
        if key:
            customer = Customer.get(key)
            self._check_account(customer.account)

        super(Controller, self).post(action, key)

    def saveAction(self, key):
        account = Account().current()

        if key:
            customer = db.get(urllib.unquote(key))  # Customer(urllib.unquote(key))
        else:
            customer = Customer()
            customer.account = account

        customer.firstname = self.request.get('firstname')
        customer.surname = self.request.get('surname')
        customer.email = self.request.get('email')
        customer.address = self.request.get('address')

        customer.put()
        self.redirect('/customer/edit/%s' % customer.key())

    def viewAction(self, key):
        account = Account().current()
        customer = db.get(key)

        self.template_values['customer'] = customer

    def editAction(self, key):
        account = Account().current()

        if key:
            customer = db.get(key)
            self.template_values['customer'] = customer

    def listAction(self, customer_key):
        account = Account().current()
        customers = Customer.gql('WHERE account = :1', account.key()).fetch(100)

        self.template_values['customer_list'] = customers

        path = os.path.join(os.path.dirname(__file__),
                            '../template/customer/list.html')
        self.response.out.write(template.render(path, self.template_values))

    def deleteAction(self, key):
        customer = Customer.get(urllib.unquote(key))
        account = Account().current()

        if customer.account.key() == account.key():
            if customer.invoices().count() == 0:
                customer.delete()
                self.redirect('/customer/list/')
            else:
                self.response.out.write('<div>you cannot delete a customer that has invoices <a href="/customer/list/>back</a></div>'
                                        )

    def generateAction(self, key):
        names = \
            """Bill Due
Ernest Desire
Evan Elpus
Hans Up
Justin Case
Pat Answer
Red Herring
Rock Bottom
Will Doo
Will Nott
Will Power
Will So
Ellen Back
May Be
Penny Worth
Hans Ohff
Lee Vitalone
Justin Time
Jack Doff
Nick Doff
Betty Wont
Mark Mywords
Owen Money
Ewen Mee
Shelby Wrightmate
Pete Sake
Iona Boat
Wendy Boatcumsin
Hugh Dunnit
Lou Sends"""

        names = names.splitlines()
        account = Account().current()

        for name in names:
            (first, sur) = name.split()

            cs = Customer()
            cs.account = account
            cs.firstname = first
            cs.surname = sur
            cs.email = '%s@%s.com' % (first.lower(), sur.lower())

            cs.address = \
                """Example Street
            190219BA
            Amsterdam"""

            self.response.out.write('<div>%s, %s, %s</div>' % (first, sur,
                                    cs.email))

            cs.put()


