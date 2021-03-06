#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import cgi
import logging
import time
import locale
import sys

sys.path.insert(0, 'reportlab.zip')

from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics

import os
import reportlab
folderFonts = os.path.dirname(reportlab.__file__) + os.sep + 'fonts'

from google.appengine.ext import webapp
from google.appengine.ext.webapp import template

from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext.webapp.util import login_required

from google.appengine.ext import db
from google.appengine.api import images
from google.appengine.api import users

import common.controller.invoice
import common.controller.company
import common.controller.customer
import common.controller.render
import common.controller.generator
import common.user

# sys.path.insert(0, 'reportlab.zip')
# try:
#    locale.setlocale(1, ('nl_NL', 'UTF8'))
# except:
#    logging.error("Unable to set locale at this point")
#

application = webapp.WSGIApplication([
    ('/company\/?(.*)/(.*)', common.controller.company.Controller),
    ('/company\/?(.*)', common.controller.company.Controller),
    ('/invoice\/?(.*)/(.*)', common.controller.invoice.Controller),
    ('/render\/?(.*)/(.*)', common.controller.render.Controller),
    ('/generator\/?(.*)/(.*)', common.controller.generator.Controller),
    ('/customer\/?(.*)/(.*)', common.controller.customer.Controller),
    ('/user\/?(.*)/(.*)', common.user.Controller),
    ('/?(.*)', common.user.Controller),
    ], debug=True)


def main():
    run_wsgi_app(application)


if __name__ == '__main__':
    main()
