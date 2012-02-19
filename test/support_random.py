
from random import randint
from common.models import *

def random_account():
    account = Account()

    account.put()
    return account

def random_company():
    company = Company()
    company.email        = 'foo@example.com'
    company.name         = 'foo'
    company.description  = '123 test'
    company.put()
    return company

def random_customer( account ):
        names = """Bill Due
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
        name  = names[randint(0, len(names)-1)]

        first, sur = name.split()
        cs = Customer()
        cs.account   = account
        cs.firstname = first
        cs.surname   = sur
        cs.email     = "%s@%s.com" % (first.lower(),sur.lower())
        cs.address = "Example Street \n190219BA\nAmsterdam"

        cs.put()

        return cs
