#!C:/Python26/python.exe

import cgitb
cgitb.enable()

import cgi
import os
import sys

import handsetdetection

def get_client_and_server_data():
    "Get environment data."
    data = {}
    data["HTTP_REFERER"] = os.environ.get("HTTP_REFERER", "")
    data["HTTP_USER_AGENT"] = os.environ.get("HTTP_USER_AGENT", "")
    data["REMOTE_ADDR"] = os.environ.get("REMOTE_ADDR", "")
    data["REQUEST_URI"] = os.environ.get("REQUEST_URI", "")
    data["SERVER_ADDR"] = os.environ.get("SERVER_ADDR", "")
    data["SERVER_NAME"] = os.environ.get("SERVER_NAME", "")
    data["user-agent"] = "Mozilla/5.0 (Linux; U; Android 2.1-update1; cs-cz; SonyEricssonX10i Build/2.1.B.0.1) AppleWebKit/530.17 (KHTML, like Gecko) Version/4.0 Mobile Safari/530.17"
    data["x-wap-profile"] = "http://wap.sonyericsson.com/UAprof/X10iR201.xml"
    return data

print("Content-type: text/html\n")
print("<html>")
print("<head><title>Hello Python API Kit</title></head>")
print("<body>")
print("<h2>Hello Python API Kit</h2>")

hd = handsetdetection

hd.set_credentials("jessie@handsetdetection.com", "4Mcy7r7wDFdCDbg2")

data = get_client_and_server_data()

try:
    result = hd.detect(data, "hd_specs")
    print("<pre style=\"white-space:pre-wrap\">")
    #sys.stdout.write(str(result))    
    sys.stdout.write("%s" % result) 
    print("</pre>")
except handsetdetection.DeviceNotFoundError, err:
    # Mobile device not detected.
    sys.stdout.write(str(None))
except handsetdetection.HandsetDetectionBaseError, err:
    # Handle the exception
    # In this script, cgitb will handle it, so raise it again.
    raise err

print("</body>")
print("</html>")