#!/usr/bin/python
# -*- coding: utf-8 -*-

from random import randint
from common.models import *


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


def random_word():
    max_len = 12
    vowels = list('qwrtypsdfghklzxcvbnm')
    consonants = list('aeouá')
#    consonants = list('aeouáéóúöüë')
    w = []
    for i in range(0, max_len):
        n_conson = randint(1, 3) % 2 + 1
        n_vowels = abs(1 - randint(1, 3) % 2) + i % 2
        w[len(w):0] = [random_char(vowels) for n in range(0, n_vowels)]
        w[len(w):0] = [random_char(consonants) for n in range(0, n_conson)]
    return ''.join(w)


def random_char(chars=None):
    if not chars:
        chars = list('abcdefghijklmnopqrstuvwxyz')
    return chars[randint(0, len(chars) - 1)]


def random_name():
    names = (
        'Bill Due',
        'Ernest Desire',
        'Evan Elpus',
        'Hans Up',
        'Justin Case',
        'Pat Answer',
        'Red Herring',
        'Rock Bottom',
        'Will Doo',
        'Will Nott',
        'Will Power',
        'Will So',
        'Ellen Back',
        'May Be',
        'Penny Worth',
        'Hans Ohff',
        'Lee Vitalone',
        'Justin Time',
        'Jack Doff',
        'Nick Doff',
        'Betty Wont',
        'Mark Mywords',
        'Owen Money',
        'Ewen Mee',
        'Shelby Wrightmate',
        'Pete Sake',
        'Iona Boat',
        'Wendy Boatcumsin',
        'Hugh Dunnit',
        'Lou Sends',
        )

    name = names[randint(0, len(names) - 1)]
    return name


