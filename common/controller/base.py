#!/usr/bin/python
# -*- coding: utf-8 -*-
from __init__ import *
from common.models import Account


class BaseController(webapp.RequestHandler):

    template_values = {}
    template_module = ''

    def get(self, action, key=None):
        if hasattr(self, '%sAction' % action.rstrip('/')):
            method = getattr(self, '%sAction' % action)
            method(key)

        self.renderTemplate(action, self.template_values)

    def post(self, action, key=None):
        if hasattr(self, '%sAction' % action.rstrip('/')):
            method = getattr(self, '%sAction' % action)
            method(key)

    def renderTemplate(self, action, template_values):
        path = os.path.join(os.path.dirname(__file__), '../../template/%s/%s.html'
                            % (self.template_module, action))

        if os.path.exists(path):
            self.response.out.write(template.render(path, self.template_values))

    def _check_account(self, account):
        current_account = Account().current()

        if current_account.key() != account.key():
            self.accessForbidden()

    def accessForbidden(self):
        self.response.out.write('You do not own that account')
        self.response.set_status(403)
        exit()
