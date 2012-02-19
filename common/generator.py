from __init__ import *
from common.models import *

class Controller( webapp.RequestHandler ):

    def get( self, action, key = None ):
        self.template_values = {}
        account = Account().current()

        if key and action in ['edit', 'save']:
            generator = Generator.get(key)
            if account.key() != generator.account.key():
                self.accessForbidden()

        if hasattr( self, "%sAction" % action.rstrip('/')):
            method = getattr( self, "%sAction" % action )
            method( key )

        self.renderTemplate( action, self.template_values )

    def post( self, action, key = None ):
        if key and action in ['edit', 'save']:
            account = Account().current()
            generator = Generator.get(key)
            if account.key() != generator.account.key():
                self.accessForbidden()

        if hasattr( self, "%sAction" % action.rstrip('/')):
            method = getattr( self, "%sAction" % action )
            method( key )

    def renderTemplate( self, action, template_values ):
        path = os.path.join(os.path.dirname(__file__), '../template/generator/%s.html' % action )
        if os.path.exists(path):
            self.response.out.write(template.render(path, self.template_values))

    def accessForbidden( self ):
        self.response.out.write( 'You do not own that account')
        self.response.set_status(403)
        exit()

    def runAction( self, key ):
        gen = Generator.get(urllib.unquote(key))
        gen.run()

        log = GeneratorLog()
        log.generator = gen
        log.text = "ran %s" % gen.description;
        log.put()

        self.redirect('/generator/edit/%s' % gen.key() )


    def saveAction( self, key ):
        account = Account().current()

        log = GeneratorLog()

        if key:
            generator = db.get( urllib.unquote(key) )
            if generator.account.key() != account.key():
                self.accessForbidden()

            log.text = "created %s" % self.request.get('description');

        else:
            generator = Generator()
            generator.account = account

            generator.company = Company.get( urllib.unquote(self.request.get('company')))
            generator.customer = Customer.get( urllib.unquote(self.request.get('customer')))
            log.text = "updated %s" % self.request.get('description');

        generator.start = datetime.strptime( self.request.get('start'), '%Y-%m-%d' )
        generator.description = self.request.get('description')
        generator.interval = int(self.request.get('interval'))

        unit = ['month', 'week', 'day']
        generator.unit = unit[unit.index(self.request.get('unit'))]

        generator.put()

        log.generator = generator;
        log.put()

        self.redirect('/generator/edit/%s' % generator.key() )

    def editAction( self, key ):
        account = Account().current()

        self.template_values['customers'] = account.customers()
        self.template_values['companies'] = account.companies()
        self.template_values['last_run']  = "never";

        if key:
            generator = Generator.get( key )
            self.template_values['key'] = key
        else:
            generator = Generator()

        if generator.lastrun:
            delta = datetime.today() - generator.lastrun
            self.template_values['last_run'] = "%d days ago" % delta.days

        self.template_values['generator'] = generator

    def deleteAction( self, key ):
        #lazy delete: should check if everything is cleaned up
        gen = Generator.get( key );

        lines = gen.lines().fetch(1000)

        db.delete( lines )

        logs = GeneratorLog.gql("WHERE generator = :1", gen.key())
        db.delete( logs.fetch(1000) )

        refs = GeneratorInvoice.gql("WHERE generator = :1", gen.key())
        db.delete( refs.fetch(1000) )

        gen.delete()

        self.redirect('/generator/list/' )


    def listAction( self, key ):
        account = Account().current()
        self.template_values['generators'] = account.generators()

    def addlineAction( self, key):
        generator = Generator.get(urllib.unquote(key))
        line = GeneratorLine()

        line.generator = generator
        line.amount = float(self.request.get('amount'))
        line.name   = self.request.get('name')

        line.put();

        #print line.key()
        #return

        self.redirect('/generator/edit/%s' % generator.key() )

    def dellineAction( self, key ):
        line = GeneratorLine.get(urllib.unquote(key))

        generator = line.generator
        line.delete()

        self.redirect('/generator/edit/%s' % generator.key() )
