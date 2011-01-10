from __init__ import *
from common.models import *

class Controller( webapp.RequestHandler ):
    #def get( self, action, key = None ):
    #    self.response.out.write('<a href="%s">logout</a>' % users.create_logout_url('/'))

    def get( self, action='login', key = None ):
        if hasattr( self, "%sAction" % action.rstrip('/')):
            method = getattr( self, "%sAction" % action )
            method( key )
        else:
            self.redirect( '/invoice/list/?tab=overdue')

        #else:
        #    self.defaultAction( key )


    #    if hasattr( self, "%sAction" % action.rstrip('/')):
    #        method = getattr( self, "%sAction" % action )
    #        method( key )
    #    else:
    #        #print "its alive!"
    #        self.loginAction( key )
    #
    #def post( self, action, key = None ):
    #    if hasattr( self, "%sAction" % action.rstrip('/')):
    #        method = getattr( self, "%sAction" % action )
    #        method( key )
    #
    def logoutAction( self, key = None ):
        self.redirect(users.create_logout_url('/'))

    #def loginAction( self, key = None ):
    #    #account = Account().current()
    #    #
    #    #if not account.companies:
    #    #    self.redirect( '/company/add/' )
    #    #
    #    #if not account.customers:
    #    #    self.redirect( '/customer/add/' )
    #
    #    self.redirect( '/invoice/list/?tab=overdue')

    #def defaultAction( self, key = None ):
    #    account = Account().current()
    #
    #    if len(account.companies()) < 1:
    #        self.redirect( '/company/add/' )
    #    elif len(account.customers()) < 1:
    #        self.redirect( '/customer/add/' )
    #    else:
    #        self.redirect( '/invoice/list/?tab=overdue')
