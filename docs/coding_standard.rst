Coding Ideas (Standards)
========================

No trailing white space anywhere.

Parentheses should have no spaces next to them::

    def good_function(self):
        pass

    def bad_function( self ):
        pass

Model code should have 100% statement coverage.

Before you do anything with an IP address (as a string or int) put it into the ipaddr library
functions IPv4Address and IPv6Address. This will standardize how things are formated, stored, and
displayed.
