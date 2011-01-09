from __init__ import *
#from common.models import customer, Invoice, Customer
from common.models import *

class Controller( webapp.RequestHandler ):
    def get( self, action, key = None ):        
        if key:
            account = Account().current()
            customer = Customer.get(key)
            if account.key() != customer.account.key():
                self.accessForbidden()

        if hasattr( self, "%sAction" % action.rstrip('/')):
            method = getattr( self, "%sAction" % action )
            method( key )

    def post( self, action, key = None ):
        if key:
            account = Account().current()
            customer = Customer.get(key)
            if account.key() != customer.account.key():
                self.accessForbidden()

        if hasattr( self, "%sAction" % action.rstrip('/')):
            method = getattr( self, "%sAction" % action )
            method( key )

    def accessForbidden( self ):
        self.response.out.write( 'You do not own that account')
        self.response.set_status(403)
        exit()
        

    def saveAction( self, key ):
        account = Account().current()

        if key:
            customer = db.get( urllib.unquote(key) ) #Customer(urllib.unquote(key))
        else:
            customer = Customer()
            customer.account = account

        customer.firstname         = self.request.get('firstname')
        customer.surname         = self.request.get('surname')
        customer.email         = self.request.get('email')
        customer.address         = self.request.get('address')

        customer.put()
        self.redirect('/customer/edit/%s' % customer.key() )

    def viewAction( self, key ):
        template_values = {};

        account = Account().current()
        customer = db.get(key)

        template_values['customer'] = customer

        path = os.path.join(os.path.dirname(__file__), '../template/customer/view.html')
        template_values['content'] = template.render( path, template_values )

        path = os.path.join(os.path.dirname(__file__), '../template/layout.html')
        self.response.out.write(template.render(path, template_values))

    def editAction( self, key ):
        template_values = {};

        account = Account().current()
        customer = db.get(key)

        template_values['customer'] = customer

        path = os.path.join(os.path.dirname(__file__), '../template/customer/edit.html')
        template_values['content'] = template.render( path, template_values )

        path = os.path.join(os.path.dirname(__file__), '../template/layout.html')
        self.response.out.write(template.render(path, template_values))

    def addAction( self, customer_key ):
        template_values = {}

        #template_values['customer'] = Customer()

        path = os.path.join(os.path.dirname(__file__), '../template/customer/edit.html')
        template_values['content'] = template.render( path, template_values )

        path = os.path.join(os.path.dirname(__file__), '../template/layout.html')
        self.response.out.write(template.render(path, template_values))

    def listAction( self, customer_key ):
        account = Account().current()
        customers = Customer.gql('WHERE account = :1', account.key()).fetch(100)

        template_values = {}
        template_values['customer_list'] = customers

        path = os.path.join(os.path.dirname(__file__), '../template/customer/list.html')
        template_values['content'] = template.render( path, template_values )

        path = os.path.join(os.path.dirname(__file__), '../template/layout.html')
        self.response.out.write(template.render(path, template_values))

    def deleteAction( self, key ):
        customer = Customer.get(urllib.unquote(key))
        account = Account().current()
        
        if customer.account.key() == account.key():
            if customer.invoices().count() == 0:
                customer.delete()
                self.redirect('/customer/list/')
            else:
                self.response.out.write('<div>you cannot delete a customer that has invoices <a href="/customer/list/>back</a></div>')

    def generateAction(self, key ):
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
        account = Account().current()

        for name in names:
            first, sur = name.split()

            cs = Customer()
            cs.account = account
            cs.firstname = first
            cs.surname   = sur
            cs.email     = "%s@%s.com" % (first.lower(),sur.lower())

            cs.address = """Example Street
            190219BA
            Amsterdam"""

            self.response.out.write('<div>%s, %s, %s</div>' % (first,sur,cs.email))


            cs.put()
