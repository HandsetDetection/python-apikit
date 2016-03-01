"""Handset Detection v4 API HDDevice tests"""
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

import datetime
import unittest
import testutils
import os.path

handsetdetection = testutils.importModule("handsetdetection")
import handsetdetection.exceptions as exceptions
from handsetdetection.HDDevice import *
from handsetdetection.HD4 import *

class HDDeviceTests(unittest.TestCase):

	@classmethod
	def setUpClass(cls):
		"""
			Need to setup some local files
			Note : Should probably only do this is the store is empty
		"""
		hd = HandsetDetection()
		#hd.communityFetchArchive()
		#fileName = os.path.join(hd.config['filesdir'], "ultimate-community.zip")
		#hd.installArchive(fileName)

	@classmethod
	def tearDownClass(cls):
		""" Purge the store """
		#store = HDStore()
		#store.purge()

	# HTTP Keys
	def test_hasBiKeysA(self):
		hdDevice = HDDevice()
		headers = {
			'user-agent' : 'Mozilla/5.0 (iPhone; U; CPU iPhone OS 4_3 like Mac OS X; en-gb) AppleWebKit/533.17.9 (KHTML, like Gecko)'
		}
		result = hdDevice.hasBiKeys(headers)
		self.assertFalse(result)

	def test_hasBiKeysA2(self):
		hdDevice = HDDevice()
		headers = {
			'x-wap-profile' : 'http://www-ccpp.tcl-ta.com/files/ALCATEL_one_touch_908.xml'
		}
		result = hdDevice.hasBiKeys(headers)
		self.assertFalse(result)

	# Android hardware headers
	def test_hasBiKeysB(self):
		hdDevice = HDDevice()
		headers = {
			'ro.product.brand' : 'Samsung',
			'ro.product.model': 'GT-I9500'
		}
		result = hdDevice.hasBiKeys(headers)
		self.assertIsNotNone(result)

	# iOS hardware headers
	def test_hasBiKeysC(self):
		hdDevice = HDDevice()
		headers = {
			'utsname.brand' : 'Apple',
			'utsname.machine': 'iMac 9,1'
		}
		result = hdDevice.hasBiKeys(headers)
		self.assertIsNotNone(result)

	# Windows hardware headers
	def test_hasBiKeysD(self):
		hdDevice = HDDevice()
		headers = {
			'devicemanufacturer' : 'Sony',
			'devicename': 'Tablet 500s'
		}
		result = hdDevice.hasBiKeys(headers)
		self.assertIsNotNone(result)

	def test_findRatingA(self):
		pass

	def test_infoStringToArrayA(self):
		pass

	def test_hardwareInfoOverlayA(self):
		pass
	
	def test_isHelperUsefulA(self):
		headers = {
			'User-Agent': 'Mozilla/5.0 (iPhone; U; CPU iPhone OS 4_3 like Mac OS X; en-gb) AppleWebKit/533.17.9 (KHTML, like Gecko)'
		}
		hdDevice = HDDevice()


		result = hdDevice.isHelperUseful(headers)
		self.assertTrue(result)

	def test_isHelperUsefulB(self):
		headers = {
			'User-Agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36'
		}

		hdDevice = HDDevice()
		result = hdDevice.isHelperUseful(headers)
		self.assertFalse(result)

if "__main__" == __name__:
    unittest.main()
