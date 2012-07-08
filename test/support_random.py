#!/usr/bin/python
# -*- coding: utf-8 -*-

from random import randint
from common.models import *


def generate_invoices(self, stub):
    from random import randint

    customers = Customer.all()
    companies = Company.all()

    for cu in customers:
        for co in companies:
            invoice = Invoice()
            invoice.company = co
            invoice.customer = cu
            invoice.description = 'hosting for http://%s.com' % cu.surname.lower()

            if randint(0, 2) > 0:
                invoice.is_billed = True
                invoice.billed = datetime.now() - timedelta(randint(1, 40))

            invoice.put()

            for i in range(0, randint(1, 5)):
                line = InvoiceLine()

                line.invoice = invoice
                line.name = 'some lorem ipsum doodie dadie dom'
                line.amount = 1.0 * randint(40, 500)
                line.put()

            self.response.out.write('<div>wrote %s, %s</div>'
                                    % (invoice.description, co.name))


def random_account():
    account = Account()

    account.put()
    return account


def random_company():
    company = Company()
    company.email = 'foo@example.com'
    company.name = 'foo'
    company.description = '123 test'
    company.put()
    return company


def random_customer(account):
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
    name = names[randint(0, len(names) - 1)]

    (first, sur) = name.split()
    cs = Customer()
    cs.account = account
    cs.firstname = first
    cs.surname = sur
    cs.email = '%s@%s.com' % (first.lower(), sur.lower())
    cs.address = '''Example Street 
190219BA
Amsterdam'''

    cs.put()

    return cs


