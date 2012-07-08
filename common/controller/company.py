from __init__ import *
from common.models import *

from base import BaseController

class Controller(BaseController):

    template_module = 'company'

    def pre_dispatch( self, action, key=None):
        if key:
            self.company = Company.get(key)
            self._check_account(self.company.account)
        else:
            self.company = Company()

    def save_action( self, key ):
        for key, prop in Company.properties().items():
            value = self.request.get(key)

            if not value:
                continue

            if type( prop ).__name__ is 'IntegerProperty':
                value = int(value)

            if type( prop ).__name__ is 'FloatProperty':
                value = float(value)

            self.company.__setattr__( key, value )

        logo = self.request.get('logo')

        if logo:
            src = images.Image(logo)
            src.horizontal_flip()
            src.horizontal_flip()
            self.company.logo = src.execute_transforms(output_encoding=images.JPEG)

        self.company.put()
        self.redirect('/company/edit/%s' % self.company.key() )

    def logo_action( self, key ):
        self.response.headers['Content-Type'] = 'image/jpg'
        self.response.headers['Content-Disposition'] = 'attachment; filename=logo.jpg'
        self.response.out.write( self.company.logo )

    def edit_action( self, key ):
        if self.company:
            self.template_values['key']        = key
        self.template_values['company'] = self.company

    def list_action( self, company_key ):
        self.template_values['companies'] =  Account().current().companies()

    def delete_action( self, key ):
        if self.company.invoices().count() > 0:
            self.response.out.write("company has invoices, delete those first")
            return

        self.company.delete();
        self.redirect('/company/list/')
