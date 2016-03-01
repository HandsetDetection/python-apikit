"""Handset Detection v4 API HDCache tests"""
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

handsetdetection = testutils.importModule("handsetdetection")
import handsetdetection.exceptions as exceptions
from handsetdetection.HDCache import *

class HDCacheTests(unittest.TestCase):
	_Cache = None
	_token = None

	def setUp(self):
		now = datetime.datetime.now()
		self._token = now.strftime("%Y%m%d%H%M%S")

	def test_CacheReadWrite(self):
		""" Test a write, read, purge """
		cache = HDCache()
		data = {}
		data = {'fish': 'snapper', 'color':'redish'}
		cache.write(self._token, data)
		cacheData = cache.read(self._token)
		self.assertEquals(cacheData, data)

		cache.purge(self._token)
		cacheData = cache.read(self._token)
		self.assertEquals(cacheData, None)

	# Note : Test requires memcached
	# pip install Python-memcached
	# Ensure memcached running on localhost
	def test_CacheDogpileMemcached(self):
		config = {
			'cache': {
				'backend': 'dogpile.cache.memcached',
				'expiry': 3600,
				'arguments' : {
					'url': '127.0.0.1:11211'
				}
			}
		}
		cache = HDCache(config)
		data = {}
		data = {'fish': 'snapper', 'color':'redish'}
		cache.write(self._token, data)
		cacheData = cache.read(self._token)
		self.assertEquals(cacheData, data)

		cache.purge(self._token)
		cacheData = cache.read(self._token)
		self.assertEquals(cacheData, None)
		
if __name__ == '__main__':
    unittest.main()