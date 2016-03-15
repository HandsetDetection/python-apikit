"""Handset Detection API Device Helper class
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

from handsetdetection.HDBase import *
from handsetdetection.HDStore import *
from handsetdetection.HDExtra import *
import os
import json

class HDDevice(HDBase):
	DETECTIONV4_STANDARD = '0'
	DETECTIONV4_GENERIC = '1'

	_device = None
	_platform = None
	_browser = None
	_app = None
	_ratingResult = None
	_Extra = None
	_Store = None
	config = {}
	
	def __init__(self, config = None):
		self._Extra = HDExtra()
		self._Store = HDStore()
		if config is not None:
			self.setConfig(config)

	def setConfig(self, config):
		for key in config['config']:
			self.config[key] = config['config'][key]

		self._Store.setConfig(config)
		self._Extra.setConfig(config)
		
	def localVendors(self):
		self.reply = {}
		self.reply['vendor'] = []
		self.setError(301, 'Nothing Found');

		deviceList = self._fetchDevices()
		if deviceList is None:
			return self.reply

		replySet = set()
		for device in deviceList:
			replySet.add(device['Device']['hd_specs']['general_vendor'])

		tmpList = list(replySet)
		tmpList.sort()
		self.reply['vendor'] = tmpList
		self.setError(0, 'OK')
		return self.reply

	def localModels(self, vendor):
		self.reply = {}
		self.reply['model'] = []
		self.setError(301, 'Nothing Found');
		
		deviceList = self._fetchDevices()
		if deviceList is None:
			return self.reply

		vendor = vendor.lower()
		replySet = set()
		for device in deviceList:
			deviceVendor = device['Device']['hd_specs']['general_vendor'].lower()
			if deviceVendor == vendor:
				replySet.add(device['Device']['hd_specs']['general_model'])
			searchKey = vendor + " "
			for alias in device['Device']['hd_specs']['general_aliases']:
				alias = alias.lower()
				if alias.find(searchKey) is 0:
					replySet.add(alias.replace(searchKey, ''))

		tmpList = list(replySet)
		tmpList.sort()
		self.reply['model'] = tmpList
		self.setError(0, 'OK')
		return self.reply

	def localView(self, vendor, model):
		self.reply = {}
		self.reply['device'] = {}
		self.setError(301, 'Nothing Found');

		deviceList = self._fetchDevices()
		if deviceList is None:
			return self.reply

		vendor = vendor.lower()
		model = model.lower()
		for device in deviceList:
			if device['Device']['hd_specs']['general_vendor'].lower() == vendor and device['Device']['hd_specs']['general_model'].lower() == model:
				self.reply['device'] = device['Device']['hd_specs']
				self.setError(0, 'OK')
		return self.reply

	def localWhatHas(self, key, value):
		self.reply = {}
		self.reply['devices'] = []
		self.setError(301, 'Nothing Found');
		
		deviceList = self._fetchDevices()
		if deviceList is None:
			return self.reply

		value = value.lower()
		for device in deviceList:
			if device['Device']['hd_specs'][key] is None:
				continue

			match = None
			if isinstance(device['Device']['hd_specs'][key], list):
				for item in device['Device']['hd_specs'][key]:
					if value.find(item.lower()) > -1:
						match = True
			elif value.find(device['Device']['hd_specs'][key].lower()) > -1:
				match = True

			if match == True:
				tmp = {}
				tmp['_id'] = device['Device']['_id']
				tmp['general_vendor'] = device['Device']['hd_specs']['general_vendor']
				tmp['general_model'] = device['Device']['hd_specs']['general_model']
				self.reply['devices'].append(tmp)

		self.setError(0, 'OK')
		return self.reply
	
	def _fetchDevices(self):
		deviceList = self._Store.fetchDevices()
		if deviceList is None:
			return self.setError(299, "Error : fetchDevices cannot read files from store.")
		return deviceList

	def localDetect(self, headers):
		newHeaders = {}
		hardwareInfo = ''

		for k in headers:
			newHeaders[k.lower()] = headers[k]

		if 'x-local-hardwareinfo' in newHeaders:
			hardwareInfo = newHeaders['x-local-hardwareinfo']
			del newHeaders['x-local-hardwareinfo']

		if self.hasBiKeys(newHeaders) is not None:
			return self.v4MatchBuildInfo(newHeaders)
		return self.v4MatchHttpHeaders(newHeaders, hardwareInfo)


	def v4MatchBuildInfo(self, headers):
		self._device = None
		self._platform = None
		self._browser = None
		self._app = None
		self._detectedRuleKey = None
		self._ratingResult = None
		self.reply = {}
		self.setError(301, 'Not Found');

		if headers is None:
			return self.reply

		self._headers = headers

		self._device = self.v4MatchBiHelper(headers, 'device')
		if self._device is None:
			return None

		self._platform = self.v4MatchBiHelper(headers, 'platform')
		if self._platform is not None:
			self.specsOverlay('platform', self._device, self._platform)

		self.reply['hd_specs'] = self._device['Device']['hd_specs']
		self.setError(0, 'OK')
		return self.reply

	def v4MatchBiHelper(self, headers, category):
		confBiKeys = self._detectionConfig[category + '-bi-order']
		if confBiKeys is None or headers is None:
			return None

		hints = []

		for platform in confBiKeys:
			value = ''
			for items in confBiKeys[platform]:
				checking = True
				for item in items:
					if item in headers:
						value = headers[item] if value == '' else value + '|' + headers[item]
					else:
						checking = False
						break
				if checking == True:
					value.strip("| \t\n\r\0\x0B")
					hints.append(value)
					subtree = self.DETECTIONV4_STANDARD if category == 'device' else category
					_id = self.getMatch('buildinfo', value, subtree, 'buildinfo', category)
					if _id is not None:
						return self.findById(_id) if category == 'device' else self._Extra.findById(_id)

		# If we get this far without a result then try a generic match
		platform = self.hasBiKeys(headers)
		if platform is not None:
			tryList = []
			tryList.append("generic|" + platform)
			tryList.append(platform + "|generic")
			for attempt in tryList:
				subtree = self.DETECTIONV4_GENERIC if category == 'device' else category
				_id = self.getMatch('buildinfo', value, subtree, 'buildinfo', category)
				if _id is not None:
					return self.findById(_id) if category == 'device' else self._Extra.findById(_id)

		return None

	def v4MatchHttpHeaders(self, headers, hardwareInfo):
		self._device = {}
		self._platform = {}
		self._browser = {}
		self._app = {}
		self._language = {}
		self._detectedRuleKey = {}
		self._ratingResult = {}
		self.reply = {}
		self.setError(301, 'Not Found');
		hwProps = {}
		deviceHeaders = {}
		extraHeaders = {}
		
		if headers is None:
			return self.reply

		if 'ip' in headers:
			del headers['ip']
		if 'host' in headers:
			del headers['host']

		# Sanitize headers & cleanup language (you filthy animal) :)
		for k in headers:
			v = headers[k].lower()
			if k == 'accept-language' or k == 'content-language':
				tmp = re.split("[,;]", v)
				k = 'language'
				if tmp is not None and len(tmp) > 0:
					v = tmp[0]
				else:
					continue
			deviceHeaders[k] = self.cleanStr(v)
			extraHeaders[k] = self.extraCleanStr(v)

		self._device = self.matchDevice(deviceHeaders)
		if self._device is None:
			return self.reply

		if hardwareInfo != '':
			hwProps = self.infoStringToArray(hardwareInfo)

		# Stop on detect set - Tidy up and return
		if self._device['Device']['hd_ops']['stop_on_detect'] == '1':
			if self._device['Device']['hd_ops']['overlay_result_specs'] == '1':
				self.hardwareInfoOverlay(self._device, hwProps)
			self.reply['hd_specs'] = self._device['Device']['hd_specs']
			self.setError(0, 'OK')
			return self.reply

		# Get extra info
		self._platform = self._Extra.matchExtra('platform', extraHeaders)
		self._browser = self._Extra.matchExtra('browser', extraHeaders)
		self._app = self._Extra.matchExtra('app', extraHeaders)
		self._language = self._Extra.matchLanguage('language', extraHeaders)

		# Find out if there is any contention on the detected rule.
		deviceList = self.getHighAccuracyCandidates()
		if deviceList is not None:

			# Resolve contention with OS check
			self._Extra._data = self._platform
			pass1List = []
			for _id in deviceList:
				tryDevice = self.findById(_id)
				if self._Extra.verifyPlatform(tryDevice['Device']['hd_specs']) is True:
					pass1List.append(_id)

			# Contention still not resolved .. check hardware
			if len(pass1List) >= 2 and hwProps is not None and len(hwProps) > 0:
				# Score the list based on hardware
				ratedResult = [];
				for _id in pass1List:
					tmp = self.findRating(_id, hwProps)
					if tmp is not None:
						ratedResult.append(tmp);

				# Find winning device by picking the one with the highest score.
				# If scores are even choose the one with the lowest distance
				winningDevice = None
				for tmpDevice in ratedResult:
					if winningDevice == None:
						winningDevice = tmpDevice
					else:
						if tmpDevice['score'] > winningDevice['score'] or (tmpDevice['score'] == winningDevice['score'] and tmpDevice['distance'] < winningDevice['distance']):
							winningDevice = tmpDevice;

				self._device = self.findById(winningDevice['_id'])

		# Overlay specs
		if self._platform is not None and 'Extra' in self._platform:
			self.specsOverlay('platform', self._device, self._platform['Extra'])
		if self._browser is not None and 'Extra' in self._browser:
			self.specsOverlay('browser', self._device, self._browser['Extra'])
		if self._app is not None and 'Extra' in self._app:
			self.specsOverlay('app', self._device, self._app['Extra'])
		if self._language is not None and 'Extra' in self._language:
			self.specsOverlay('language', self._device, self._language['Extra'])

		# Overlay hardware info result if required
		if (self._device['Device']['hd_ops']['overlay_result_specs'] == 1 or self._device['Device']['hd_ops']['overlay_result_specs'] == '1') and hardwareInfo != '':
			self.hardwareInfoOverlay(self._device, hwProps)

		self.reply['hd_specs'] = self._device['Device']['hd_specs']
		self.setError(0, 'OK')
		return self.reply

	def findRating(self, deviceId, props):
		""" Rates a device as compared to a set of hardware properties

		deviceId string - A device ID
		props dict - A dictionary of properties
		return dictionary
		"""
		device = self.findById(deviceId)
		if device is None:
			return None

		specs = device['Device']['hd_specs']
		total = 0;
		result = {}

		# Display Resolution - Worth 40 points if correct
		if 'display_x' in props and 'display_y' in props:
			total += 40
			if int(specs['display_x']) == int(props['display_x']) and int(specs['display_y']) == int(props['display_y']):
				result['resolution'] = 40
			elif int(specs['display_x']) == int(props['display_y']) and int(specs['display_y']) == int(props['display_x']):
				result['resolution'] = 40
			elif float(specs['display_pixel_ratio']) > 1.0:
				# The resolution can be scaled by the pixel ratio for some devices
				adjX = int(int(props['display_x']) * float(specs['display_pixel_ratio']))
				adjY = int(int(props['display_y']) * float(specs['display_pixel_ratio']))
				if int(specs['display_x']) == adjX and int(specs['display_y']) == adjY:
					result['resolution'] = 40
				elif int(specs['display_x']) == adjY and int(specs['display_y']) == adjX:
					result['resolution'] = 40

		# Display pixel ratio - Also worth 40 points

		if 'display_pixel_ratio' in props:
			total += 40;
			# Note : display_pixel_ratio will be a string stored as 1.33 or 1.5 or 2, perhaps 2.0 ..
			if specs['display_pixel_ratio'] == str(round(props['display_pixel_ratio']/100, 2)):
				result['display_pixel_ratio'] = 40;

		# Benchmark - 10 points - Enough to tie break but not enough to overrule display or pixel ratio.
		if 'benchmark' in props:
			total += 10;
			if 'benchmark_min' in specs and 'benchmark_max' in specs:
				if int(props['benchmark']) >= int(specs['benchmark_min']) and int(props['benchmark']) <= int(specs['benchmark_max']):
					# Inside range
					result['benchmark'] = 10
				else:
					# Outside range
					result['benchmark'] = 0

		result['score'] = 0 if total == 0 else int(sum(result.values()))
		result['possible'] = total;

		# Distance from mean used in tie breaking situations if two devices have the same score.
		result['distance'] = 100000
		if 'benchmark_min' in specs and 'benchmark_max' in specs and 'benchmark' in props:
			result['distance'] = int(abs(((specs['benchmark_min'] + specs['benchmark_max'])/2) - props['benchmark']))

		result['_id'] = deviceId
		return result

	def specsOverlay(self, category, device, specs):
		"""Overlays specs onto a device
		
		category string - 'platform' | 'browser' | 'app' | 'language
		device object - A device dictionary
		"""
		if category == "platform":
			if specs['hd_specs']['general_platform'] != "":
				device['Device']['hd_specs']['general_platform'] = specs['hd_specs']['general_platform'];
				device['Device']['hd_specs']['general_platform_version'] = specs['hd_specs']['general_platform_version'];
		elif category == 'browser':
			if specs['hd_specs']['general_browser'] != "":
				device['Device']['hd_specs']['general_browser'] = specs['hd_specs']['general_browser'];
				device['Device']['hd_specs']['general_browser_version'] = specs['hd_specs']['general_browser_version'];
		elif category == 'app':
			if specs['hd_specs']['general_app'] != "":
				device['Device']['hd_specs']['general_app'] = specs['hd_specs']['general_app'];
				device['Device']['hd_specs']['general_app_version'] = specs['hd_specs']['general_app_version'];
				device['Device']['hd_specs']['general_app_category'] = specs['hd_specs']['general_app_category'];
		elif category == 'language':
			if specs['hd_specs']['general_language'] != "":
				device['Device']['hd_specs']['general_language'] = specs['hd_specs']['general_language'];
				device['Device']['hd_specs']['general_language_full'] = specs['hd_specs']['general_language_full'];
		#return device ??


	def infoStringToArray(self, hardwareInfo):
		"""
			Takes a string of onDeviceInformation and turns it into something that can be used for high accuracy checking.
			Strings a usually generated from cookies, but may also be supplied in headers.
			The format is $w:$h:$r:$b where w is the display width, h is the display height, r is the pixel ratio and b is the benchmark.
				display_x, display_y, display_pixel_ratio, general_benchmark
				
			@param string $hardwareInfo String of light weight device property information, separated by ':'
			@return dictionary partial specs array of information we can use to improve detection accuracy
		"""
		# Remove the header or cookie name from the string 'x-specs1a='
		if hardwareInfo.find('=') > -1:
			cookieName, hardwareInfo = hardwareInfo.split('=')

		reply = {}
		info = hardwareInfo.split(":")
		if len(info) != 4:
			return reply
		reply['display_x'] = int(info[0])
		reply['display_y'] = int(info[1])
		reply['display_pixel_ratio'] = int(info[2])
		reply['benchmark'] = int(info[3])
		return reply;

	def hardwareInfoOverlay(self, device, info):
		"""Overlays hardware info onto a device - Used in generic replys
		device dictionary
		info dictionary
		"""
		if 'display_x' in info and info['display_x'] != 0:
			device['Device']['hd_specs']['display_x'] = info['display_x']
		if 'display_y' in info and info['display_y'] != 0:
			device['Device']['hd_specs']['display_y'] = info['display_y']
		if 'display_pixel_ratio' in info and info['display_pixel_ratio'] != 0:
			device['Device']['hd_specs']['display_pixel_ratio'] = str(round(float(info['display_pixel_ratio'] / 100), 2))
		# return device ??
		
	def matchDevice(self, headers):
		"""
		Device matching

		Plan of attack :
			1) Look for opera headers first - as they're definitive
			2) Try profile match - only devices which have unique profiles will match.
			3) Try user-agent match
			4) Try other x-headers
			5) Try all remaining headers
		"""
		# May need to assign headers to an interneal variable - not sure if its pass by ref or value ...
		# Remember the agent for generic matching later.
		agent = ""

		# Opera mini sometimes puts the vendor # model in the header - nice! ... sometimes it puts ? # ? in as well
		if 'x-operamini-phone' in headers and headers['x-operamini-phone'] != "? # ?":
			_id = self.getMatch('x-operamini-phone', headers['x-operamini-phone'], self.DETECTIONV4_STANDARD, 'x-operamini-phone', 'device')
			if _id is not None:
				return self.findById(_id)
			agent = headers['x-operamini-phone']
			del headers['x-operamini-phone']

		# Profile header matching
		if 'profile' in headers:
			_id = self.getMatch('profile', headers['profile'], self.DETECTIONV4_STANDARD, 'profile', 'device')
			if _id is not None:
				return self.findById(_id)
			del headers['profile']

		# Profile header matching - native header name
		if 'x-wap-profile' in headers:
			_id = self.getMatch('profile', headers['x-wap-profile'], self.DETECTIONV4_STANDARD, 'x-wap-profile', 'device')
			if _id is not None:
				return self.findById(_id)
			del headers['x-wap-profile']


		# Match nominated headers ahead of x- headers, but do check x- headers
		order = self._detectionConfig['device-ua-order']
		for k in headers:
			if k not in order and k.startswith("x-"):
				order.append(k)

		for item in order:
			if item in headers:
				self.log("Trying user-agent match on header " + item)
				_id = self.getMatch('user-agent', headers[item], self.DETECTIONV4_STANDARD, item, 'device')
				if _id is not None:
					return self.findById(_id)

		# Generic matching - Match of last resort
		self.log('Trying Generic Match')

		_id = None
		if 'x-operamini-phone-ua' in headers:
			_id = self.getMatch('agent', headers['x-operamini-phone-ua'], self.DETECTIONV4_GENERIC, 'agent', 'device')
		if 'agent' in headers and _id is None:
			_id = self.getMatch('user-agent', headers['agent'], self.DETECTIONV4_GENERIC, 'agent', 'device')
		if 'user-agent' in headers and _id is None:
			_id = self.getMatch('user-agent', headers['user-agent'], self.DETECTIONV4_GENERIC, 'agent', 'device')

		if _id is not None:
			return self.findById(_id)

		return None

	def findById(self, _id):
		return self._Store.read("Device_" + _id)

	def getHighAccuracyCandidates(self):
		""" Determines if High Accuracy checks are available on the device which was just detected """
		branch = self.getBranch('hachecks')
		ruleKey = self._detectedRuleKey['device'] if 'device' in self._detectedRuleKey else None;
		if ruleKey in branch:
			return branch[ruleKey]
		return None

	def isHelperUseful(self, headers):
		""" Determines of hd4Helper would prove more accurate detection results """
		if headers is None:
			return None

		if self.localDetect(headers) is None:
			return None

		if self.getHighAccuracyCandidates() is None:
			return None

		return True
