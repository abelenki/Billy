#!/usr/bin/env python
# coding=UTF-8
import sys
import os
import time
import reportlab
import StringIO

from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen.canvas import Canvas

#import reportlab
from reportlab.pdfgen import canvas
##from pdfmetrics import standardEncodings
#
#from reportlab.pdfbase import pdfmetrics


from reportlab.lib.pagesizes import letter
from reportlab.lib.pagesizes import A4

from datetime import datetime
from datetime import timedelta


class Invoice( object ):
    canvas = None
    invoice = None
    size = (0,0)
    col = 80
    row = 600
    default_font = ( 'Helvetica', 10 )


    def __init__( self, invoice, output, size=A4 ):
        self.canvas = canvas.Canvas(output, pagesize=size)
        self.invoice = invoice
        self.size = size

    def save( self ):
        self.getHeader()
        self.getBillingLines()
        self.getFooter()

        return self.canvas.save()

    def getBillingLines( self ):
        font, size = self.default_font
        self.canvas.setFont(font, size)
        cost, total = 0, 0

        self.setRow(365)

        for line in self.invoice.billing_introduction().splitlines():
            self.canvas.drawString(self.getCol(), self.getRow(), line );
            self.nextRow()

        self.nextRow()
        self.nextRow()

        for line in self.invoice.invoice_lines():
            #dot = unicode('•')
            total = total + line.amount
            self.canvas.drawString( 435, self.getRow(), "€%s" % str.rjust("%0.2f" % line.amount,17) )
            self.canvas.drawString( self.getCol(), self.getRow(), "%s" % line.name )
            self.nextRow()

        self.canvas.line(435,self.getRow(),505,self.getRow())
        self.canvas.drawString(self.getCol(), self.nextRow(), "Subtotaal")
        self.canvas.drawString(435, self.getRow(),
                                        "€%s" % str.rjust("%0.2f" % total,17) )


        self.canvas.drawString(self.getCol(), self.nextRow(),
                                        "%0.2f%% BTW" % (self.invoice.get_vat() * 100))
        self.canvas.drawString(435, self.getRow(),
                        "€%s" % str.rjust("%0.2f" % (total*self.invoice.get_vat()),17))

        total = total + (total*self.invoice.get_vat())

        self.nextRow(10)
        self.canvas.line(435,self.getRow(),505,self.getRow())
        self.nextRow(20)

        self.canvas.setFont( 'Helvetica-Bold', 10 )
        self.canvas.drawString(self.getCol(), self.getRow(), "Totaal" )
        self.canvas.drawString(435, self.getRow(),
                                            "€%s" % str.rjust("%0.2f" % total,17))


    def getHeader( self ):
        r,g,b = (0.4, 0.7, 0.3)
        width, height = self.size
        font, size = self.default_font

        if self.invoice.company.logo:
            image = canvas.ImageReader(StringIO.StringIO(self.invoice.company.logo))
            self.canvas.drawImage( image, 435, height-180, 130, 165 )

        self.canvas.setFont( '%s-Bold' % font, 16 )
        self.canvas.drawString( 435, height - 265, 'Factuur' )

        self.canvas.setFont( font, size )

        self.setCol(80)
        self.setRow(140)

        customer = self.invoice.customer

        self.canvas.drawString(self.getCol(), self.getRow(),
            "%s %s" % (customer.firstname, customer.surname) );

        self.nextRow()

        address = customer.address.splitlines()
        for line in address:
            self.canvas.drawString( self.getCol(), self.getRow(), line.strip() );
            self.nextRow()

        # plaats, datum
        self.setRow(260)

        self.canvas.setFillColorRGB(r,g,b);

        self.canvas.drawString( self.getCol(), self.getRow(), "plaats, datum" )
        self.canvas.drawString( self.getCol()+200, self.getRow(), "factuur nummer" )

        self.nextRow()
        self.canvas.setFillColorRGB(0,0,0);

        billed = datetime.now()

        if self.invoice.billed:
            billed = self.invoice.billed

        self.canvas.drawString( self.getCol(), self.getRow(),
            "%s, %s" % (self.invoice.company.city, billed.strftime('%e %B %Y')) )

        self.canvas.drawString( self.getCol()+200, self.getRow(), "%s" % self.invoice.billing_number() )

        self.nextRow()
        self.nextRow()
        self.canvas.setFillColorRGB(r,g,b);
        self.canvas.drawString( self.getCol(), self.getRow(), "betreft" )
        self.nextRow()
        self.canvas.setFillColorRGB(0,0,0);
        self.canvas.drawString( self.getCol(), self.getRow(), self.invoice.description )


        #
        #self.canvas.drawString(self.getCol(), self.getRow(),
        #        "%s, %s" % ( self.invoice.company.city, self.invoice.billing_date(format)) )
        #


    def getBillingDate(self, format="%e %B %Y"):
        self.canvas.drawString(self.getCol(), self.getRow(),
                "%s, %s" % ( self.invoice.company.city, self.invoice.billing_date(format)) )

        self.canvas.drawString(self.getCol(), self.getRow(),
                "F-%s" % "HOEPLA" )


        #self.canvas.drawString(self.getCol()+200, self.getRow(),
        #                    "F-%s" % self.invoice.billing_number() )

        self.nextRow()
        self.nextRow()

        self.canvas.setFillColorRGB(r,g,b);
        self.canvas.drawString(self.getCol(), self.getRow(), "betreft" )

        self.nextRow()
        self.canvas.setFillColorRGB(0,0,0);
        self.canvas.drawString(self.getCol(), self.getRow(), "Hosting" )

        self.nextRow(45)


    def getFooter( self ):
        #w, height = self.size
        self.canvas.setFont( 'Helvetica-Bold', 9 )
        self.setRow( 780 )
        self.setCol( 80 )

        lines = self.invoice.company.footer.splitlines() #str.split( self.invoice.footer, "\n")

        for line in lines:
            self.canvas.drawString( self.getCol(), self.getRow(), str.center( str(line), 100 ));
            self.nextRow()

    def getCol(self):
        return self.col

    def setCol(self,num):
        self.col = num
        return self.col

    def getRow(self):
        return self.row

    def setRow( self, num ):
        width, height = self.size

        self.row = height - num
        return self.row

    def nextRow(self, increase = 15 ):
        self.row = self.row - increase

        return self.row
