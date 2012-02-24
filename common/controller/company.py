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

    def saveAction( self, key ):
        company = self.company
        properties = Company.properties()

        for key, prop in properties.items():
            value = self.request.get(key)

            if not value:
                continue
            
            if type( prop ).__name__ is 'IntegerProperty':
                value = int(value)

            if type( prop ).__name__ is 'FloatProperty':
                value = float(value)

            company.__setattr__( key, value )

        logo = self.request.get('logo')

        if logo:
            src = images.Image(logo)
            src.horizontal_flip()
            src.horizontal_flip()
            company.logo = src.execute_transforms(output_encoding=images.JPEG)

        company.put()
        self.redirect('/company/edit/%s' % company.key() )

    def logoAction( self, key ):
        self.response.headers['Content-Type'] = 'image/jpg'
        self.response.headers['Content-Disposition'] = 'attachment; filename=logo.jpg'
        self.response.out.write( self.company.logo )

    def editAction( self, key ):
        if self.company:
            self.template_values['key']        = key
        self.template_values['company'] = self.company

    def listAction( self, company_key ):
        self.template_values['companies'] =  Account().current().companies()

    def deleteAction( self, key ):
        if self.company.invoices().count() > 0:
            self.response.out.write("company has invoices, delete those first")
            return

        self.company.delete();
        self.redirect('/company/list/')
