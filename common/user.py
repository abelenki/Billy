#!/usr/bin/python
# -*- coding: utf-8 -*-

from __init__ import *
from common.models import *

# FIXME this code has been broken due api changes?


class Controller(webapp.RequestHandler):

    def get(self, action='upgrade', key=None):
        logging.debug('user get')
        if hasattr(self, '%sAction' % action.rstrip('/')):
            method = getattr(self, '%sAction' % action)
            method(key)
        elif action == '':
            self.upgradeAction(key)
        else:

            self.redirect('/invoice/list/?tab=overdue')

    def post(self, action, key=None):
        if hasattr(self, '%sAction' % action.rstrip('/')):
            method = getattr(self, '%sAction' % action)
            method(key)

    def inviteAction(self, key):
        email = self.request.get('email')

        logging.debug('entering invite %s' % email)

        # google.appengine.api.mail.is_email_valid()

        if mail.is_email_valid(email):
            logging.debug('saving invite %s', email)
            account = Account().get(key)
            user = users.get_current_user()
            description = self.request.get('description')

            invite = AccountInvite(user=user, account=account, email=email,
                                   description=description)

            invite.put()

            body = \
                '''%s wants you to join Billy:

%s
Click on this link to join:
%s''' \
                % (user.nickname(), description,
                   'https://blizzapp.appspot.com/user/accept/%s' % invite.key())

            mail.send_mail(sender=user.email(), to=email, subject=description,
                           body=body)

        self.redirect('/user/account/%s' % key)

    def revokeAction(self, key):
        user = users.get_current_user()

        invite = db.get(key)
        account = invite.account

        # only account owners may do this

        if invite.account.user != user:
            self.redirect('/user/account/%s' % account.key())
            return
        else:
            invite.delete()
            self.redirect('/user/account/%s' % account.key())

    def acceptAction(self, key):
        user = users.get_current_user()

        invite = db.get(key)

        if invite.email == user.email():
            au = AccountUser(user=user, account=invite.account)
            au.put()

            invite.delete()
            self.redirect('/user/account/%s' % invite.account.key())

        self.redirect('/user/accounts/')

    def logoutAction(self, key=None):
        self.redirect(users.create_logout_url('/'))

    def accountsAction(self, key=None):
        user = users.get_current_user()

        accounts = db.Query(AccountUser).filter('user =', user)

        preferred = self.request.get('preferred')

        if self.request.method == 'POST':
            for a in accounts:
                is_pref = True and str(a.key()) == preferred or False
                a.is_preferred = is_pref
                a.put()

        template_values = {}
        template_values['accounts'] = accounts
        template_values['invites'] = db.Query(AccountInvite).filter('email =',
                user.email())

        path = os.path.join(os.path.dirname(__file__),
                            '../template/user/accounts.html')
        template_values['content'] = template.render(path, template_values)

        path = os.path.join(os.path.dirname(__file__), '../template/layout.html')
        self.response.out.write(template.render(path, template_values))

    def accountAction(self, key):

        account = Account.get(key)

        # print account.invites().count()
        #
        # exit()

        template_values = {}

        template_values['account'] = account
        template_values['users'] = account.users()
        template_values['user'] = users.get_current_user()

        path = os.path.join(os.path.dirname(__file__),
                            '../template/user/account.html')
        template_values['content'] = template.render(path, template_values)

        path = os.path.join(os.path.dirname(__file__), '../template/layout.html')
        self.response.out.write(template.render(path, template_values))

    def upgradeAction(self, key=None):
        user = users.get_current_user()

        au_list = db.Query(AccountUser).filter('user =', user)

        if not au_list.get():
            logging.debug('start upgrade')
            a_list = db.Query(Account).filter('user =', user)

            for a in a_list:
                logging.debug('add account user')
                ac = AccountUser(account=a, user=user)
                ac.put()

            logging.debug('done')
        else:
            logging.debug('no upgrade needed')
            self.redirect('/invoice/list/?tab=overdue')


        # account = Account().current()
        # acs = AccountCompany.gql('WHERE account = :1', account )
        #
        # logging.debug(acs)
        #
        # if not acs.fetch(1):
        #    logging.debug("start upgrade path")
        #
        #    companies = Company.gql('WHERE account = :1', account )
        #
        #    for c in companies:
        #        ac = AccountCompany( company=c, account=account )
        #        ac.put()
        #
        #    account.current_company = c
        #    account.put()
        #
        #    logging.debug('upgrade complete')
        # else:
        #    logging.debug('upgrade already done')
        #    self.redirect( '/invoice/list/?tab=overdue')
