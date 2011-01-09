from __init__ import *
from common.models import *

class Controller( webapp.RequestHandler ):
    def get( self, action, key = None ):
        if hasattr( self, "%sAction" % action.rstrip('/')):
            method = getattr( self, "%sAction" % action )
            method( key )
        else:
            self.listAction( key )

    def post( self, action, key = None ):
        if hasattr( self, "%sAction" % action.rstrip('/')):
            method = getattr( self, "%sAction" % action )
            method( key )

    def saveAction( self, key ):
        if key:
            company = Company.get(key)
            company.billnr_template = self.request.get('billnr_template')
            company.city         = self.request.get('city')
            company.postcode      = self.request.get('postcode')
            company.address      = self.request.get('address')
            company.country      = self.request.get('country')
            company.bankaccount  = self.request.get('bankaccount')
            company.footer       = self.request.get('footer')
            company.introduction = self.request.get('introduction')
            
            logo = self.request.get('logo')
            
            if logo:
                src = images.Image(logo)
                src.horizontal_flip()
                src.horizontal_flip()
                company.logo = src.execute_transforms(output_encoding=images.JPEG)

        else:
            company = Company()

        company.email         = self.request.get('email')
        company.name         = self.request.get('name')
        company.description  = self.request.get('description')
        company.put()

        self.redirect('/company/edit/%s' % company.key() )

    def logoAction( self, key ):
        company = Company.get(key)
        self.response.headers['Content-Type'] = 'image/jpg'
        self.response.headers['Content-Disposition'] = 'attachment; filename=logo.jpg'

        self.response.out.write( company.logo )

    def editAction( self, key ):
        template_values = {};
        
        if key:
            company = Company.get(key)
            #template_values['upload_url'] = blobstore.create_upload_url('/company/upload/%s' % key )            
            template_values['key']        = key
        else:
            company = Company()
        
        template_values['company'] = company

        path = os.path.join(os.path.dirname(__file__), '../template/company/edit.html')
        template_values['content'] = template.render( path, template_values )
        
        path = os.path.join(os.path.dirname(__file__), '../template/layout.html')
        self.response.out.write(template.render(path, template_values))

    def viewAction( self, key ):
        template_values = {}

        company = db.get(key)
        account = Account().current()

        template_values['company'] = company
        #template_values['customers'] = account.customers()
        #template_values['invoices']  = company.invoices()

        path = os.path.join(os.path.dirname(__file__), '../template/company/view.html')
        template_values['content'] = template.render( path, template_values )

        path = os.path.join(os.path.dirname(__file__), '../template/layout.html')
        self.response.out.write(template.render(path, template_values))

    def listAction( self, company_key ):
        account = Account().current()
        companies = Company.gql('WHERE account = :1', account)

        template_values = {}
        template_values['companies'] = companies

        path = os.path.join(os.path.dirname(__file__), '../template/company/list.html')
        template_values['content'] = template.render( path, template_values )

        path = os.path.join(os.path.dirname(__file__), '../template/layout.html')
        self.response.out.write(template.render(path, template_values))

    def deleteAction( self, key ):
        company = Company.get( urllib.unquote(key))
        
        if company.invoices().count() > 0:
            self.response.out.write("company has invoices, delete those first")
            return

        #for invoice in company.invoices():
        #    invoice.delete()
        company.delete();
        self.redirect('/company/list/')

