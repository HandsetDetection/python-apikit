"""Handset Detection API implementation

The HandsetDetection class provides easy access to the Handset Detections HTTP
API version 4.
"""
# Copyright (c) 2009 -2016 Teleport Corp Pty Ltd.
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
#

import json
import urllib2
import urlparse
import io
import socket
import ConfigParser
import os.path
import string
import zipfile
import yaml
import time
import md5

import exceptions as exceptions
from handsetdetection.HDStore import *
from handsetdetection.HDDevice import *

class HandsetDetection(object):
    "An object for accessing the Handset Detection API v4.0"

    configFile = 'hd_config.yml'
    config = {
        'api_username': '',
        'api_secret': '',
        'api_server': 'api.handsetdetection.com',
        'site_id': '0',
        'use_local': False,
        'filesdir': '/tmp',
        'debug': False,
        'cache_requests': False,
        'timeout': 5,
        'use_proxy': False,
        'proxy_server': '',
        'proxy_port' : '',
        'proxy_user' : '',
        'proxy_pass': '',
        'retries': 3
    }
    _api_realm = 'APIv4'
    _urlPathFragment = "/apiv4"
    _Store = None
    _raw_reply = ''
    
    # Initialization
    def __init__(self, configFile = None):
        self._Store = HDStore()
        self._Device = HDDevice()
        if configFile is not None:
            self.readConfig(configFile)
        elif os.path.isfile(self.configFile):
            self.readConfig(self.configFile)

    # Public Methods
    def getReply(self):
        return self.reply
    
    def getRawReply(self):
        return self._raw_reply
    
    def readConfig(self, configFileName):
        """Configure the api kit with details from a config file.

        configFileName string - The name of config file
        """
        yamlFile = open(configFileName)
        config = yaml.safe_load(yamlFile)
        yamlFile.close()
        self.setConfig(config)

    def setConfig(self, config):
        """Set the username and generate the user token.

        api_username string - your registered e-mail address
        api_secret string - the auto-generated API version 2 secret
        """
        for key in config['config']:
            self.config[key] = config['config'][key]

        self._Store.setConfig(config)
        self._Device.setConfig(config)
        
    def deviceVendors(self):
        "Returns a list of vendors."

        if self.config['use_local'] is True or self.config['use_local'] is 1:
            self.reply = self._Device.localVendors()
            self._raw_reply = json.dumps(self.reply)
        else:
            uriParts = [ self._urlPathFragment, "device", "vendors", self.config['site_id'] ]
            uri = string.join(uriParts, "/") + ".json"
            self._do_request(uri, {}, {}, "json")
        return self.reply

    def deviceModels(self, vendorName):
        """Returns a list of models for the given vendor.
        
        vendorName string - The name of a vendor eg. Nokia
        """

        if self.config['use_local'] is True or self.config['use_local'] is 1:
            self.reply = self._Device.localModels(vendorName)
            self._raw_reply = json.dumps(self.reply)
        else:
            uriParts = [ self._urlPathFragment, "device", "models", vendorName, self.config['site_id'] ]
            uri = string.join(uriParts, "/") + ".json"  
            self._do_request(uri, {}, {}, "json")
        return self.reply

    def deviceWhatHas(self, key, value):

        if self.config['use_local'] is True or self.config['use_local'] is 1:
            self.reply = self._Device.localWhatHas(key, value)
            self._raw_reply = json.dumps(self.reply)
        else:
            uriParts = [ self._urlPathFragment, "device", "whathas", key, value, self.config['site_id'] ]
            uri = string.join(uriParts, "/") + ".json"  
            self._do_request(uri, {}, {}, "json")
        return self.reply
        
    def deviceView(self, vendor, model):

        if self.config['use_local'] is True or self.config['use_local'] is 1:
            self.reply = self._Device.localView(vendor, model)
            self._raw_reply = json.dumps(self.reply)
        else:
            uriParts = [ self._urlPathFragment, "device", "view", vendor, model, self.config['site_id'] ]
            uri = string.join(uriParts, "/") + ".json"
            self._do_request(uri, {}, {}, "json")
        return self.reply
        
    def deviceDetect(self, data, options = None):
        """Detect a handset with the User-Agent and/or other information.

        data - a dictionary containing a User-Agent, IP address, x-wap-profile,
               and any other information that may be useful in identifying the
               handset
        options - a string or list of options to be returned from your query,
                  e.g., "geoip,product_info,display" or ["geoip",
                  "product_info"], etc.
        """
        assert isinstance(data, dict)

        if self.config['use_local'] is True or self.config['use_local'] is 1:
            self.reply = self._Device.localDetect(data)
            self._raw_reply = json.dumps(self.reply)
        else:
            # Set Content-type header
            headers = {}
            headers["Content-type"] = "application/json"
            uriParts = [ self._urlPathFragment, "device", "detect", self.config['site_id'] ]
            uri = string.join(uriParts, "/") + ".json"
    
            if isinstance(options, list):
                options = ",".join(options)
            data["options"] = options
            self._do_request(uri, headers, data, "json")
            
        return self.reply

    def deviceFetchArchive(self):
        """Fetch an archive of all the device specs and install it
        """
        
        uriParts = [ self._urlPathFragment, "device", "fetcharchive", self.config['site_id'] ]
        uri = string.join(uriParts, "/")
        result = self._do_request(uri, {}, {}, "zip")
        if result == None:
            return None

        # Save Archive
        zipFileName = os.path.join(self.config['filesdir'], "ultimate-full.zip")
        with open(zipFileName, 'wb') as zipFile:
            zipFile.write(self._raw_reply)
        zipFile.close()
        
        # Install archive
        self.installArchive(zipFileName)
    
    def communityFetchArchive(self):
        """Fetch the community device archive.
        """
        uriParts = [ self._urlPathFragment, "community", "fetcharchive", self.config['site_id'] ]
        uri = string.join(uriParts, "/")
        result = self._do_request(uri, {}, {}, "zip")
        if result == None:
            return None
        
        # Save Archive
        zipFileName = os.path.join(self.config['filesdir'], "ultimate-community.zip")
        with open(zipFileName, 'wb') as zipFile:
            zipFile.write(self._raw_reply)
        zipFile.close()
        
        # Install Archive
        self.installArchive(zipFileName)
        
    def installArchive(self, fileName):
        "Install an archive"
        
        zf = zipfile.ZipFile(fileName, 'r')        
        for archiveFile in zf.namelist():
            zf.extract(archiveFile, self.config['filesdir'])
            srcFileName = os.path.join(self.config['filesdir'], archiveFile)
            self._Store.moveIn(srcFileName, archiveFile)
              
    # Private methods

    def _do_request(self, uri, headers, data, replyType):
        "Send the request to Handset Detection."

        self._raw_reply = ''
        self.reply = {}
        
        postdata = json.dumps(data)
        url = "http://" + self.config['api_server'] + uri
        
        # Note : Precompute the auth digest to avoid the challenge turnaround request
        # Speeds up network turnaround requests by 50%
        realm = self._api_realm
        username = self.config['api_username']
        secret = self.config['api_secret']
        nc = "00000001"
        snonce = self._api_realm
        cnonce = md5.new(str(int(time.time())) + secret).hexdigest()
        qop = 'auth'
        # AuthDigest Components
        # http://en.wikipedia.org/wiki/Digest_access_authentication
        ha1 = md5.new(username + ':' + realm + ':' + secret).hexdigest()
        ha2 = md5.new('POST:' + uri).hexdigest()
        response = md5.new(ha1 + ':' + snonce + ':' + nc + ':' + cnonce + ':' + qop + ':' + ha2).hexdigest()

        socket.setdefaulttimeout(self.config['timeout'])
        # Conventional HTTP Digest handling
        #auth = urllib2.HTTPDigestAuthHandler()
        #auth.add_password(self._api_realm, url, self.config['api_username'], self.config['api_secret'])
        #opener = urllib2.build_opener(auth, urllib2.HTTPHandler(debuglevel=1))
        #urllib2.install_opener(opener)
        request = urllib2.Request(url, postdata, headers)
        request.add_header('Authorization',
                            'Digest ' +
                            'username="' + username + '", ' +
                            'realm="' + realm + '", ' +
                            'nonce="' + snonce + '", ' +
                            'uri="' + uri + '", ' +
                            'qop=' + qop + ', ' +
                            'nc=' + nc + ', ' +
                            'cnonce="' + cnonce + '", ' +
                            'response="' + response + '", ' +
                            'opaque="' + realm + '"'
                           )
        response = urllib2.urlopen(request)
        rawReply = response.read()
        
        if response.code == 200:
            #print rawReply
            self._raw_reply = rawReply
            if replyType == "json":
                self.reply = json.loads(rawReply)
            return True
        assert False, ("response.code != 200 - urllib2 should have thrown an exception.")
