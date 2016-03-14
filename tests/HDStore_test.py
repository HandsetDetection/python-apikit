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
import os.path

handsetdetection = testutils.importModule("handsetdetection")
import handsetdetection.exceptions as exceptions
from handsetdetection.HDStore import *

class HDStoreTests(unittest.TestCase):
	_Cache = None
	_token = None
	_data = {
		'roses': 'red',
		'fish': 'blue',
		'sugar': 'sweet',
		'number': 4
	}
	
	_deviceA = {
		'_id' : 999999,
		'hd_specs' : {
			'general_vendor': 'Samsung',
			'general_model': 'Galaxy S27'
		},
		'comment': 'Unit testing device'
	}

	_deviceB = {
		'_id' : 999998,
		'hd_specs' : {
			'general_vendor': 'Samsung',
			'general_model': 'Galaxy S28'
		},
		'comment': 'Unit testing device'
	}

	def setUp(self):
		now = datetime.datetime.now()
		self._token = now.strftime("%Y%m%d%H%M%S")

	def test_readWrite(self):
		key = 'readkey-' + self._token
		store = HDStore()
		store.write(key, self._data)
		data = store.read(key)
		self.assertEquals(data, self._data)

		# Verify data is cached
		data = store._Cache.read(key)
		self.assertEquals(data, self._data)

		# Verify data is on disk
		exists =  os.path.isfile(os.path.join(store._directory, key+'.json'))
		self.assertTrue(exists);

	def test_storeFetch(self):
		key = 'storekey-' + self._token
		store = HDStore()
		store.store(key, self._data)
		data = store.fetch(key)
		self.assertEquals(self._data, data)

		# Verify data is not cached
		data = store._Cache.read(key)
		self.assertEquals(data, None)

		# Verify data is on disk
		exists =  os.path.isfile(os.path.join(store._directory, key+'.json'))
		self.assertTrue(exists);

	def test_FetchDevices(self):
		store = HDStore({'config':{'filesdir':'/tmp/hd40test'}})
		store.write('Device_' + str(self._deviceA['_id']), self._deviceA)
		store.write('Device_' + str(self._deviceB['_id']), self._deviceB)
		devices = store.fetchDevices()
		count = 0
		for key in devices:
			count += 1
		self.assertEquals(2, count)

	def test_moveIn(self):
		store = HDStore({'config':{'filesdir':'/tmp/hd40test'}})
		store.purge()
		deviceA = store.read('Device_' + str(self._deviceA['_id']))
		self.assertEquals(None, deviceA)

		# Save dict as Json - try moving it into the store, then fetching it back out.
		fileName = 'Device_' + str(self._deviceA['_id']) + '.json'
		jsonFile = open(fileName, "w")
		jsonFile.write(json.dumps(self._deviceA))
		jsonFile.close()
		store.moveIn(fileName, fileName)
		deviceA = store.fetch('Device_' + str(self._deviceA['_id']))
		self.assertEquals(self._deviceA, deviceA)
		
		# Cleanup
		store.purge()
		pass
	
if __name__ == '__main__':
    unittest.main()