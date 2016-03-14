"""Handset Detection API Extra Helper class
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

from HDBase import *
from HDStore import *
import os
import json

class HDExtra(HDBase):
	_data = None
	_Store = None
	config = {}
	
	def __init__(self, config = None):
		self._Store = HDStore()
		if config is not None:
			self.setConfig(config)

	def setConfig(self, config):
		for key in config['config']:
			self.config[key] = config['config'][key]
		self._Store.setConfig(config)

	def set(self, data):
		self._data = data

	def matchExtra(self, category, headers):
		""" Matches all HTTP header extras - platform, browser and app """
		order = self._detectionConfig[category + '-ua-order']

		# Match nominated headers ahead of x- headers, but do check x- headers
		for k in headers:
			if k not in order and k.startswith("x-"):
				order.append(k)

		for item in order:
			if item in headers:
				self.log("Trying user-agent match on header " + item)
				_id = self.getMatch('user-agent', headers[item], category, item, category)
				if _id is not None:
					return self.findById(_id)

		return None

	def findById(self, _id):
		""" Find an extra by its id """
		return self._Store.read("Extra_" + _id)

	def matchLanguage(self, category, headers):
		""" Find the language, preferebly from a language header, but try the user-agent as a last resort """
		extra = {}

		# Mock up a fake Extra for merge into detection reply.
		extra['_id'] = '0'
		extra['Extra'] = {}
		extra['Extra']['hd_specs'] = {}
		extra['Extra']['hd_specs']['general_language'] = ''
		extra['Extra']['hd_specs']['general_language_full'] = ''

		# Try directly from http header first
		if 'language' in headers:
			candidate = headers['language']
			if candidate in self._detectionLanguages:
				extra['Extra']['hd_specs']['general_language'] =  candidate
				extra['Extra']['hd_specs']['general_language_full'] = self._detectionLanguages[candidate]
				return extra

		order = self._detectionConfig['language-ua-order']
		for k in headers:
			if k not in order:
				order.append(k)

		languageList = self._detectionLanguages

		for headerKey in order:
			if headerKey in headers:
				agent = headers[headerKey]

				if agent is not None:
					for code in languageList:
						if re.search('[; \(]' + code + '[; \)]', agent, re.I) is not None:
							extra['Extra']['hd_specs']['general_language'] =  code
							extra['Extra']['hd_specs']['general_language_full'] = languageList[code]
							return extra
		return None
	
	def verifyPlatform(self, specs):
		"""
			Returns false if this device definitively cannot run this platform and platform version.
			Returns true if its possible of if there is any doubt.

			Note : The detected platform must match the device platform. This is the stock OS as shipped
			on the device. If someone is running a variant (eg CyanogenMod) then all bets are off.

		"""
		if self._data is None:
			return None
		
		platform = self._data
		platformName = platform['Extra']['hd_specs']['general_platform'].strip().lower()
		platformVersion = platform['Extra']['hd_specs']['general_platform_version'].strip().lower()
		devicePlatformName = specs['general_platform'].strip().lower()
		devicePlatformVersionMin = specs['general_platform_version'].strip().lower()
		devicePlatformVersionMax = specs['general_platform_version_max'].strip().lower()

		# Its possible that we didnt pickup the platform correctly or the device has no platform info
		# Return true in this case because we cant give a concrete false (it might run this version).
		if platform is None or platformName == '' or devicePlatformName == '':
			return True

		# Make sure device is running stock OS / Platform
		# Return true in this case because its possible the device can run a different OS (mods / hacks etc..)
		if platformName != devicePlatformName:
			return True

		# Detected version is lower than the min version - so definetly false.
		if platformVersion != '' and devicePlatformVersionMin != '' and self.comparePlatformVersions(platformVersion, devicePlatformVersionMin) <= -1:
			return False

		# Detected version is greater than the max version - so definetly false.
		if platformVersion != '' and devicePlatformVersionMax != '' and self.comparePlatformVersions(platformVersion, devicePlatformVersionMax) >= 1:
			return False

		# Maybe Ok ..
		return True

	def comparePlatformVersions(self, va, vb):
		"""
			Compares two platform version numbers
			return < 0 if a < b, 0 if a == b and > 0 if a > b : Also returns 0 if data is absent from either.
		"""
		if va is None or va == '' or vb is None or vb == '':
			return 0

		versionA = self.breakVersionApart(va)
		versionB = self.breakVersionApart(vb)

		major = self.compareSmartly(versionA['major'], versionB['major'])
		minor = self.compareSmartly(versionA['minor'], versionB['minor'])
		point = self.compareSmartly(versionA['point'], versionB['point'])

		if major != 0:
			return major
		if minor != 0:
			return minor
		if point != 0:
			return point
		return 0

	def breakVersionApart(self, versionNumber):
		"""
			Breaks a version number apart into its major, minor and point release numbers for comparison.
			Big Assumption : That version numbers separate their release bits by '.' !!!
			might need to do some analysis on the string to rip it up right, but this assumption seems to hold... for now.
		"""
		versionNumber = versionNumber + '.0.0.0'
		tmp = versionNumber.split('.', 4)
		reply = {}
		reply['major'] = tmp[0] if tmp[0] is not None and tmp[0] != '' else '0'
		reply['minor'] = tmp[1] if tmp[1] is not None and tmp[1] != '' else '0'
		reply['point'] = tmp[2] if tmp[2] is not None and tmp[2] != '' else '0'
		return reply

	def compareSmartly(self, a, b):
		"""
			Helper for comparing two strings (numerically if possible)
		"""
		a = unicode(a)
		b = unicode(b)
		if a.isnumeric() and b.isnumeric():
			return int(a) - int(b)
		if a < b:
			return -1
		if a > b:
			return 1
		return 0