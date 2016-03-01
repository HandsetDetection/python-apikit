"""Handset Detection API Storage Helper class
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

from HDCache import *
import os
import json
import sys
from collections import OrderedDict
import pprint

class HDStore(object):
	_dirname = "hd40store"
	_directory = ""
	_cache = None
	_deviceList = None
	config = {
		'config' : {
			'filesdir' : '/tmp',
		}
	}

	# Initialization
	def __init__(self, config = None):
		self._Cache = HDCache()
		if config is not None:
			self.setConfig(config)
		else:
			self.setConfig(self.config)

	def setConfig(self, config):
		""" Sets config options """
		for key in config['config']:
			self.config[key] = config['config'][key]

		self._directory = os.path.join(self.config['filesdir'], self._dirname)
		if not os.path.exists(self._directory):
			os.makedirs(self._directory)
			
		self._Cache.setConfig(config)

	def write(self, key, data):
		"""
		string - key
		object - data
		"""
		if data is None:
			return None

		if self.store(key, data) is None:
			return None

		return self._Cache.write(key, data)

	def store(self, key, value):
		try:
			jsonFile = open(os.path.join(self._directory, key) + '.json', "w")
			jsonFile.write(json.dumps(value))
			jsonFile.close()
		except:
			return None
		return True

	def read(self, key):
		data = self._Cache.read(key)
		if data is not None:
			return data

		data = self.fetch(key)
		if data is None:
			return None

		if self._Cache.write(key, data) is None:
			raise ValueError('Cache not writeable - is it OK ? Here is the config' + str(self._Cache.config))

		return data

	def fetch(self, key):
		try:
			jsonFile = open(os.path.join(self._directory, key) + '.json', "r")
			jsonStr = jsonFile.read();
			jsonFile.close();
			if key.startswith('Device') or key.startswith('Extra'):
				return json.loads(jsonStr)
			return json.loads(jsonStr, object_pairs_hook=OrderedDict)
		except:
			return None

	def moveIn(self, src, dest):
		os.rename(src, os.path.join(self._directory, dest))
	
	def purge(self):
		for fileName in os.listdir(self._directory):
			os.remove(os.path.join(self._directory, fileName))
			key = os.path.splitext(fileName)[0]
			self._Cache.purge(key)

	# Dictionary ordering not required on devices - just detection trees
	def fetchDevices(self):
		if self._deviceList is not None:
			return self._deviceList
		
		devices = []
		for fileName in os.listdir(self._directory):
			if fileName.find('Device') is 0:
				jsonFile = open(os.path.join(self._directory, fileName), "r")
				jsonStr = jsonFile.read();
				jsonFile.close();
				devices.append(json.loads(jsonStr))
		self._deviceList = devices
		return devices

