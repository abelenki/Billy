from __init__ import *

class Account( db.Model ):
    user        = db.UserProperty()
    send_mail   = db.BooleanProperty(default=False)
    _companies = None
    _customers = None
    _generators = None

    def get_current( self ):
        return Account.current()

    def current(self):
        user = users.get_current_user()

        current = Account.gql('WHERE user = :1', user ).get()

        if not current:
            current = Account()
            current.user = user
            current.put()

        return current

    def generators( self ):
        if not self._generators:
            self._generators = Generator.gql('WHERE account= :1', self.key() ).fetch(100)

        return self._generators


    def customers( self ):
        if not self._customers:
            self._customers = Customer.gql('WHERE account= :1', self.key() ).fetch(100)

        return self._customers

    def companies( self ):
        if not self._companies:
            self._companies = Company.gql('WHERE account= :1', self.key() ).fetch(100)

        return self._companies


class Company( db.Model ):
    account         = db.ReferenceProperty( Account, default=Account().current() )
    name            = db.StringProperty( multiline=False )
    email           = db.EmailProperty()
    description     = db.StringProperty( multiline=True, default='')
    bankaccount     = db.StringProperty( multiline=False, default='')
    accountname     = db.StringProperty( multiline=False )
    coc_number      = db.StringProperty( multiline=False )
    vat_number      = db.StringProperty( multiline=False )
    address         = db.StringProperty( multiline=True )
    postcode        = db.StringProperty( multiline=False )
    city            = db.StringProperty( multiline=False )
    country         = db.StringProperty( multiline=False )
    billnr_template = db.StringProperty(multiline=False,default='%Y%%05d')
    billnr_start    = db.IntegerProperty(default=0)
    payment_term    = db.IntegerProperty(default=16)
    vat             = db.FloatProperty( default=0.19 )
    logo            = db.BlobProperty()

    footer          = db.StringProperty( multiline=True, default='')
    introduction    = db.StringProperty( multiline=True, default="Dear $name,\nThis invoice concerns $description")

    def invoices( self, offset=0, limit=100 ):
        return Invoice.gql("WHERE company = :1", self.key() )

class Customer( db.Model ):
    account     = db.ReferenceProperty( Account )
    firstname   = db.StringProperty( multiline=False )
    surname     = db.StringProperty( multiline=False )
    email       = db.EmailProperty()
    address     = db.StringProperty( multiline=True )

    def invoices( self ):
        return  Invoice.gql("WHERE customer = :1", self)

    def fullname(self,fmt="{surname}, {firstname}"):
        return '%s, %s' % ( self.surname, self.firstname )
        ##return "{surname}, {firstname}".format(surname=self.surname,firstname=self.firstname)
        #return fmt.format(surname=self.surname,firstname=self.firstname)

class Generator( db.Model ):
    account     = db.ReferenceProperty( Account, default=Account().current() )
    company     = db.ReferenceProperty( Company )
    customer    = db.ReferenceProperty( Customer )

    created     = db.DateTimeProperty(auto_now_add=True)
    lastrun     = db.DateTimeProperty()
    start       = db.DateTimeProperty(auto_now_add=True)
    interval    = db.IntegerProperty(default=1)
    count       = db.IntegerProperty(default=0)
    unit        = db.StringProperty(multiline=False,default='month')

    description = db.StringProperty( multiline=False, default='')

    def lines( self ):
        return GeneratorLine.gql("WHERE generator = :1", self.key())

    def run( self ):
        if not self.lastrun:
            self.lastrun = self.start


        today = datetime.now()

        if self.unit == 'month':
            count = 0
            while True:
                month = ( self.lastrun.month + count ) % 12
                if month == 0: month = 12
                year  = self.lastrun.year + int(count/12)
                date = self.lastrun.replace(year=year,month=month)
                count = count + self.interval

                if date.date() < today.date():
                    #print "date < today", date.date(), today.date()
                    self.generate_invoice( date )
                else:
                    break;
        else:
            if self.unit == 'week':
                delta = timedelta(weeks=self.interval)
            else:
                delta = timedelta(days=self.interval)

            date = self.lastrun

            while True:
                if date < today:
                    self.generate_invoice(date)
                else:
                    break;
                date = date + delta

        self.lastrun = today # last time run
        self.count = self.count + 1
        self.put()


    def generate_invoice( self, invoice_date ):
        #print 'generate invoice for %s' % invoice_date.date()
        invoice = Invoice()

        invoice.account = self.account
        invoice.company = self.company
        invoice.customer = self.customer

        invoice.description = self.description
        invoice.created     = invoice_date

        invoice.put()

        for gen_line in self.lines():
            line = InvoiceLine()
            line.invoice = invoice
            line.name    = gen_line.name
            line.amount  = gen_line.amount
            line.put()

        log = GeneratorInvoice(invoice=invoice,generator=self)
        log.put()


class GeneratorLine( db.Model ):
    generator   = db.ReferenceProperty( Generator )
    name        = db.StringProperty(multiline=False)
    amount      = db.FloatProperty()

class Invoice( db.Model ):
    account     = db.ReferenceProperty( Account, default=Account().current() )
    company     = db.ReferenceProperty( Company )
    customer    = db.ReferenceProperty( Customer )

    description = db.StringProperty( multiline=False, default='')
    billed      = db.DateTimeProperty()
    modified    = db.DateTimeProperty( auto_now=True )
    created     = db.DateTimeProperty( auto_now_add=True )
    payed       = db.DateTimeProperty()
    bill_number = db.StringProperty( multiline=False)
    is_payed    = db.BooleanProperty()
    is_billed   = db.BooleanProperty()

    def invoice_logs( self ):
        return InvoiceLog.gql("WHERE invoice = :1", self.key())

    def invoice_lines( self ):
        return InvoiceLine.gql("WHERE invoice = :1", self.key())

    def billing_number( self ):
        if not self.bill_number:
            if self.billed == None:
                return None
            else:
                num = Invoice.gql('WHERE company = :1 AND bill_number != NULL', self.company).count()+1 # ('-bill_number').get().bill_number + 1
                num = self.company.billnr_start + num
                num = time.strftime(self.company.billnr_template) % num
                self.bill_number = num;
                self.put()

        return self.bill_number

    def billing_introduction(self):
        intro = string.Template(self.company.introduction)

        values = dict(
            name="%s %s" % (self.customer.firstname, self.customer.surname),
            description=self.description
        )

        return intro.substitute(values)

    def get_vat( self ):
        return self.company.vat

    def status(self):
        if self.is_payed:
            return 2
        if self.billed:
            now = datetime.now()
            if ( self.billed + timedelta(16) ) < now:
                return 5 #OVERDUE
            if ( self.billed + timedelta(9) ) < now:
                return 4 #HALFWAY DUE

            return 3
        return 1

    def duedate(self):
        if self.billed:
            billed = self.billed + timedelta(16)
            return billed.date()
        return "not billed yet"

class InvoiceLine( db.Model ):
    invoice     = db.ReferenceProperty( Invoice )
    created     = db.DateTimeProperty( auto_now_add=True )
    modified    = db.DateTimeProperty( auto_now=True )
    name        = db.StringProperty(multiline=False)
    amount      = db.FloatProperty()

class InvoiceLog( db.Model ):
    invoice     = db.ReferenceProperty( Invoice )
    text        = db.StringProperty(multiline=False)
    created     = db.DateTimeProperty( auto_now_add=True )

class GeneratorLog( db.Model ):
    generator     = db.ReferenceProperty( Generator )
    text        = db.StringProperty(multiline=False)
    created     = db.DateTimeProperty( auto_now_add=True )

class GeneratorInvoice( db.Model ):
    generator   = db.ReferenceProperty( Generator )
    invoice     = db.ReferenceProperty( Invoice )
    created     = db.DateTimeProperty( auto_now_add=True )
