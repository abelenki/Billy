from __init__ import *
from common.models import *
from common import render

class Controller( webapp.RequestHandler ):
    def get( self, action, key = None ):
        account = Account().current()

        if not account.companies():
            self.redirect( '/company/add/' )

        if not account.customers():
            self.redirect( '/customer/add/' )


        if hasattr( self, "%sAction" % action.rstrip('/')):
            method = getattr( self, "%sAction" % action )
            method( key )

    def post( self, action, key = None ):
        if hasattr( self, "%sAction" % action.rstrip('/')):
            method = getattr( self, "%sAction" % action )
            method( key )

    def saveAction( self, key ):
        if self.request.method == 'POST':
            log = InvoiceLog()

            if not key:
                invoice = Invoice()
                invoice.company = db.get( self.request.get( 'company' ) );
                log.text = "save: created new invoice '%s'" % self.request.get('description')

                #invoice.customer = db.get( self.request.get( 'customer' ) );
            else:
                invoice = Invoice.get( key );
                log.text = "save: saved '%s'" % invoice.description

            invoice.customer = db.get( self.request.get( 'customer' ) );
            invoice.description = self.request.get( 'description' );

            if key:
                if self.request.get('is_payed'):
                    log.text = "save: marked invoice payed"
                    #print self.request.get('is_payed')
                    #return
                    #invoice.is_payed = True
                    invoice.payed = datetime.now()
                else:
                    log.text = "save: unmarked invoice payed"
                    invoice.payed = None #datetime.now()
                    invoice.is_payed = False

                if self.request.get( 'payed' ):
                    invoice.payed = datetime.strptime( self.request.get('payed'), '%Y-%m-%d')

                if self.request.get( 'is_billed' ):
                    #log.text = "save: set invoice to billed"
                    invoice.billed = datetime.now()

                if self.request.get( 'billed' ):
                    invoice.billed = datetime.strptime( self.request.get('billed'), '%Y-%m-%d')
                    log.text = "save: set invoice to billed %s" % invoice.billed.date()

            invoice.put()
            log.invoice = invoice;
            log.put()
            self.redirect( '/invoice/edit/%s' % invoice.key() )

    def addlineAction( self, key ):
        line = InvoiceLine()

        line.invoice = Invoice.get(key);
        line.name = self.request.get('name')
        #print self.request.get('amount')

        line.amount = 1.0 * float(self.request.get('amount'))
        line.put();

        self.redirect('/invoice/edit/%s' % key )

    def savelineAction( self, key ):
        line = InvoiceLine.get( key );

        line.name = self.request.get( 'name' )
        line.amount = float(self.request.get( 'amount' ))

        line.put()

        self.redirect( '/invoice/edit/%s' % line.invoice.key() )

    def dellineAction( self, key ):
        line = InvoiceLine.get( key )
        invoice = line.invoice

        line.delete()

        self.redirect( '/invoice/edit/%s' % invoice.key() )


    def viewAction( self, key ):
        template_values = {}

        invoice = db.get(key)
        account = Account().current()

        template_values['invoice'] = invoice
        template_values['customers'] = account.customers()
        template_values['invoices']  = invoice.invoices(0,10)



        path = os.path.join(os.path.dirname(__file__), '../template/invoice/view.html')
        template_values['content'] = template.render( path, template_values )

        path = os.path.join(os.path.dirname(__file__), '../template/layout.html')
        self.response.out.write(template.render(path, template_values))


    def listAction( self, invoice_key ):
        template_values = {};
        account = Account().current()

        gql = []

        tab = self.request.get('tab')

        if tab == 'overdue':
            invoices = Invoice.gql('where billed < :1 and billed != null and account = :2 order by billed asc', (datetime.now() - timedelta(16)), account)
        elif tab == 'billed':
            invoices = Invoice.gql('where billed != null and payed = null and account = :1 order by billed asc', account)
        elif tab == 'payed':
            invoices = Invoice.gql('where payed != null and account = :1 order by payed asc', account)
        else:
            tab = 'all'
            invoices = Invoice.gql('where account = :1 order by billed asc', account )

        template_values['tab']      = tab
        template_values['invoices'] = invoices

        path = os.path.join(os.path.dirname(__file__), '../template/invoice/list.html')
        template_values['content'] = template.render( path, template_values )

        path = os.path.join(os.path.dirname(__file__), '../template/layout.html')
        self.response.out.write(template.render(path, template_values))

    def deleteAction( self, key ):
        invoice = Invoice.get( urllib.unquote(key))

        for line in invoice.invoice_lines():
            line.delete()


        invoice.delete();
        self.redirect('/invoice/list/')

    def editAction( self, key ):
        template_values = {};
        account = Account().current()

        template_values['customers'] = account.customers()
        template_values['companies'] = Company.gql('WHERE account = :1', account )

        if key:
            invoice = Invoice.get( key )
            total = sum( line.amount for line in invoice.invoice_lines() );
            template_values['invoice_total'] = total
            template_values['key'] = key



            if invoice.customer:
                template_values['customer_key'] = invoice.customer.key()

            if invoice.is_payed:
                template_values['payed']    = invoice.payed.strftime('%Y-%m-%d');

            if invoice.billed:
                template_values['billed']   = invoice.billed.strftime('%Y-%m-%d');
        else:
            invoice = Invoice()

            if self.request.get('customer'):
                #print self.request.get('customer')
                template_values['customer_key'] = self.request.get('customer')


        template_values['invoice'] = invoice

        path = os.path.join(os.path.dirname(__file__), '../template/invoice/edit.html')
        template_values['content'] = template.render( path, template_values )
        path = os.path.join(os.path.dirname(__file__), '../template/layout.html')
        self.response.out.write(template.render(path, template_values))

    def mailAction( self, key ):
        template_values = {}
        account = Account().current()

        output = StringIO.StringIO()
        invoice = Invoice.get( urllib.unquote(key) );
        customer = invoice.customer

        invoice = Invoice.get( urllib.unquote(key) )
        invoice_render = render.Invoice( invoice, output )


        filename = "%s_%s-%s.pdf" % (
            invoice.customer.firstname.replace(' ', '_'),
            invoice.customer.surname.replace(' ', '_'),
            invoice.billing_number()
        )

        invoice_render.save()

        mail.send_mail(
            sender=invoice.company.email,
            to="%s <%s>" % ( customer.fullname(), customer.email ),
            subject=invoice.description,
            body=invoice.billing_introduction(),
            attachments=[(filename,output.getvalue())]
        )

        log = InvoiceLog()
        log.text = "mail: send invoice per mail to %s" % invoice.company.email
        log.invoice = invoice
        log.put()

        self.redirect('/invoice/list/')

    def renderAction( self, key ):
        temlate_values = {}


        invoice = Invoice.get( urllib.unquote(key) )
        invoice_render = render.Invoice( invoice, self.response.out )

        filename = "%s_%s-%s.pdf" % (
            invoice.customer.firstname.replace(' ', '_'),
            invoice.customer.surname.replace(' ', '_'),
            invoice.billing_number()
        )


        self.response.headers['Content-Type'] = 'application/pdf'
        self.response.headers['Content-Disposition'] = 'attachment; filename=%s' % filename

        invoice_render.save()

    def generateAction(self,stub):
        from random import randint
        customers = Customer.all();
        companies = Company.all();

        for cu in customers:
            for co in companies:
                invoice = Invoice();
                invoice.company = co
                invoice.customer = cu
                invoice.description = "hosting for http://%s.com" % cu.surname.lower()

                if randint(0,2) > 0:
                    invoice.billed = datetime.now() - timedelta(randint(1,40))

                invoice.put()


                for i in range(0,randint(1,5)):
                    line = InvoiceLine()

                    line.invoice = invoice;
                    line.name = "some lorem ipsum doodie dadie dom"
                    line.amount = 1.0 * randint(40,500)
                    line.put();

                self.response.out.write('<div>wrote %s, %s</div>' % (invoice.description, co.name))
