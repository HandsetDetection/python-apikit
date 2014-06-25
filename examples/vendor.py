#!C:/Python26/python.exe
"A CGI script listing mobile device vendors."
# Copyright (c) 2009 Teleport Corp Pty Ltd.
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

# Written by Troy Farrell <troy@entheossoft.com>
# Created: 20090811

# This makes debugging errors easier.
import cgitb
cgitb.enable()

import cgi
import sys

# If you installed handsetdetection as a Python egg outside of the normal
# Python path, put that path in sys.path:
#sys.path.append("/PATH/TO/handsetdetection-1.0-pyPYTHONVERSION.egg")

import handsetdetection

def list_vendors(data):
    "Return a response to the browser."
    items = ["<li>%s</li>" % cgi.escape(i) for i in data]
    vendors = "\n            ".join(items)
    result = """Content-type: text/html;charset=UTF-8

<!DOCTYPE html>
<html>
    <head>
        <title>Mobile Device Vendors</title>
        <meta http-equiv="Content-type" content="text/html;charset=UTF-8" />
    </head>
    <body>
        <p>
            This is a list of mobile device vendors.
        </p>
        <ul>
            %s
        </ul>
    </body>
</html>""" % vendors
    sys.stdout.write(result)

def main():
    "Show a list of mobile device vendors."
    # First, get the information to pass to Handset Detection.
    hd = handsetdetection
    hd.set_credentials("jessie@handsetdetection.com", "4Mcy7r7wDFdCDbg2")
    try:
        result = hd.vendor()
        list_vendors(result)
    except handsetdetection.HandsetDetectionBaseError, err:
        # Handle the exception
        # In this script, cgitb will handle it, so raise it again.
        raise err

if "__main__" == __name__:
    main()

# Some CGI handlers don't know what to do with a byte-order mark ("bomb").
# vim:set nobomb et sw=4 ts=4 tw=79:
