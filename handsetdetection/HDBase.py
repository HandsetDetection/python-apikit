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

import os
import logging
import re

class HDBase(object):
	_tree = {}
	_store = None
	_detectionv4_standard = 0
	_detectionv4_generic = 1
	_detectedRuleKey = {}
	_deviceUAFilter = " _\\#-,./:\"'"
	_extraUAFilter = " "
	_loggerHost = 'logger.handsetdetection.com';
	_loggerPort = 80;
	_detectionConfig = {
		'device-ua-order': ['x-operamini-phone-ua', 'x-mobile-ua', 'device-stock-ua', 'user-agent', 'agent'],
		'platform-ua-order': ['x-operamini-phone-ua', 'x-mobile-ua', 'device-stock-ua', 'user-agent', 'agent'],
		'browser-ua-order': ['user-agent', 'agent', 'device-stock-ua'],
		'app-ua-order': ['user-agent', 'agent', 'device-stock-ua'],
		'language-ua-order': ['user-agent', 'agent', 'device-stock-ua'],
		'device-bi-order': {
			'android': [
				['ro.product.brand','ro.product.model'],
				['ro.product.manufacturer','ro.product.model'],
				['ro-product-brand','ro-product-model'],
				['ro-product-manufacturer','ro-product-model'],
			],
			'ios': [
				['utsname.brand','utsname.machine']
			],
			'windows phone': [
				['devicemanufacturer','devicename']
			]
		},
		'platform-bi-order': {
			'android': [
				['ro.build.id', 'ro.build.version.release'],
				['ro-build-id', 'ro-build-version-release'],
			],
			'ios': [
				['uidevice.systemName','uidevice.systemversion']
			],
			'windows phone': [
				['osname','osversion']
			]
		},
		'browser-bi-order': {},
		'app-bi-order': {}
	}

	_detectionLanguages = {
		'af': 'Afrikaans',
		'sq': 'Albanian',
		'ar-dz': 'Arabic (Algeria)',
		'ar-bh': 'Arabic (Bahrain)',
		'ar-eg': 'Arabic (Egypt)',
		'ar-iq': 'Arabic (Iraq)',
		'ar-jo': 'Arabic (Jordan)',
		'ar-kw': 'Arabic (Kuwait)',
		'ar-lb': 'Arabic (Lebanon)',
		'ar-ly': 'Arabic (libya)',
		'ar-ma': 'Arabic (Morocco)',
		'ar-om': 'Arabic (Oman)',
		'ar-qa': 'Arabic (Qatar)',
		'ar-sa': 'Arabic (Saudi Arabia)',
		'ar-sy': 'Arabic (Syria)',
		'ar-tn': 'Arabic (Tunisia)',
		'ar-ae': 'Arabic (U.A.E.)',
		'ar-ye': 'Arabic (Yemen)',
		'ar': 'Arabic',
		'hy': 'Armenian',
		'as': 'Assamese',
		'az': 'Azeri',
		'eu': 'Basque',
		'be': 'Belarusian',
		'bn': 'Bengali',
		'bg': 'Bulgarian',
		'ca': 'Catalan',
		'zh-cn': 'Chinese (China)',
		'zh-hk': 'Chinese (Hong Kong SAR)',
		'zh-mo': 'Chinese (Macau SAR)',
		'zh-sg': 'Chinese (Singapore)',
		'zh-tw': 'Chinese (Taiwan)',
		'zh': 'Chinese',
		'hr': 'Croatian',
		'cs': 'Czech',
		'da': 'Danish',
		'da-dk': 'Danish',
		'div': 'Divehi',
		'nl-be': 'Dutch (Belgium)',
		'nl': 'Dutch (Netherlands)',
		'en-au': 'English (Australia)',
		'en-bz': 'English (Belize)',
		'en-ca': 'English (Canada)',
		'en-ie': 'English (Ireland)',
		'en-jm': 'English (Jamaica)',
		'en-nz': 'English (New Zealand)',
		'en-ph': 'English (Philippines)',
		'en-za': 'English (South Africa)',
		'en-tt': 'English (Trinidad)',
		'en-gb': 'English (United Kingdom)',
		'en-us': 'English (United States)',
		'en-zw': 'English (Zimbabwe)',
		'en': 'English',
		'us': 'English (United States)',
		'et': 'Estonian',
		'fo': 'Faeroese',
		'fa': 'Farsi',
		'fi': 'Finnish',
		'fr-be': 'French (Belgium)',
		'fr-ca': 'French (Canada)',
		'fr-lu': 'French (Luxembourg)',
		'fr-mc': 'French (Monaco)',
		'fr-ch': 'French (Switzerland)',
		'fr': 'French (France)',
		'mk': 'FYRO Macedonian',
		'gd': 'Gaelic',
		'ka': 'Georgian',
		'de-at': 'German (Austria)',
		'de-li': 'German (Liechtenstein)',
		'de-lu': 'German (Luxembourg)',
		'de-ch': 'German (Switzerland)',
		'de-de': 'German (Germany)',
		'de': 'German (Germany)',
		'el': 'Greek',
		'gu': 'Gujarati',
		'he': 'Hebrew',
		'hi': 'Hindi',
		'hu': 'Hungarian',
		'is': 'Icelandic',
		'id': 'Indonesian',
		'it-ch': 'Italian (Switzerland)',
		'it': 'Italian (Italy)',
		'it-it': 'Italian (Italy)',
		'ja': 'Japanese',
		'kn': 'Kannada',
		'kk': 'Kazakh',
		'kok': 'Konkani',
		'ko': 'Korean',
		'kz': 'Kyrgyz',
		'lv': 'Latvian',
		'lt': 'Lithuanian',
		'ms': 'Malay',
		'ml': 'Malayalam',
		'mt': 'Maltese',
		'mr': 'Marathi',
		'mn': 'Mongolian (Cyrillic)',
		'ne': 'Nepali (India)',
		'nb-no': 'Norwegian (Bokmal)',
		'nn-no': 'Norwegian (Nynorsk)',
		'no': 'Norwegian (Bokmal)',
		'or': 'Oriya',
		'pl': 'Polish',
		'pt-br': 'Portuguese (Brazil)',
		'pt': 'Portuguese (Portugal)',
		'pa': 'Punjabi',
		'rm': 'Rhaeto-Romanic',
		'ro-md': 'Romanian (Moldova)',
		'ro': 'Romanian',
		'ru-md': 'Russian (Moldova)',
		'ru': 'Russian',
		'sa': 'Sanskrit',
		'sr': 'Serbian',
		'sk': 'Slovak',
		'ls': 'Slovenian',
		'sb': 'Sorbian',
		'es-ar': 'Spanish (Argentina)',
		'es-bo': 'Spanish (Bolivia)',
		'es-cl': 'Spanish (Chile)',
		'es-co': 'Spanish (Colombia)',
		'es-cr': 'Spanish (Costa Rica)',
		'es-do': 'Spanish (Dominican Republic)',
		'es-ec': 'Spanish (Ecuador)',
		'es-sv': 'Spanish (El Salvador)',
		'es-gt': 'Spanish (Guatemala)',
		'es-hn': 'Spanish (Honduras)',
		'es-mx': 'Spanish (Mexico)',
		'es-ni': 'Spanish (Nicaragua)',
		'es-pa': 'Spanish (Panama)',
		'es-py': 'Spanish (Paraguay)',
		'es-pe': 'Spanish (Peru)',
		'es-pr': 'Spanish (Puerto Rico)',
		'es-us': 'Spanish (United States)',
		'es-uy': 'Spanish (Uruguay)',
		'es-ve': 'Spanish (Venezuela)',
		'es': 'Spanish (Traditional Sort)',
		'es-es': 'Spanish (Traditional Sort)',
		'sx': 'Sutu',
		'sw': 'Swahili',
		'sv-fi': 'Swedish (Finland)',
		'sv': 'Swedish',
		'syr': 'Syriac',
		'ta': 'Tamil',
		'tt': 'Tatar',
		'te': 'Telugu',
		'th': 'Thai',
		'ts': 'Tsonga',
		'tn': 'Tswana',
		'tr': 'Turkish',
		'uk': 'Ukrainian',
		'ur': 'Urdu',
		'uz': 'Uzbek',
		'vi': 'Vietnamese',
		'xh': 'Xhosa',
		'yi': 'Yiddish',
		'zu': 'Zulu'
	}

	def __init__(self):
		#TODO setup deviceUAFilterList && extraUAFilterList
		pass
	
	def setError(self, status, message):
		self.reply['status'] = status
		self.reply['message'] = message
		if status is not 0:
			return None
		return True

	def extraCleanStr(self, headerString):
		headerString = headerString.lower()
		for char in self._extraUAFilter:
			headerString = headerString.replace(char,'')
		headerString = re.sub(r'[^(\x20-\x7F)]*', '', headerString)
		headerString = headerString.strip()
		return headerString

	def cleanStr(self, headerString):
		headerString = headerString.lower()
		for char in self._deviceUAFilter:
			headerString = headerString.replace(char,'')
		headerString = re.sub(r'[^(\x20-\x7F)]*', '', headerString)
		headerString = headerString.strip()
		return headerString

	def log(self, msg):
		logging.warning(msg)

	def hasBiKeys(self, headers):
		if 'agent' in headers:
			return None
		if 'user-agent' in headers:
			return None
		if 'profile' in headers:
			return None
		if 'x-wap-profile' in headers:
			return None
		
		biKeys = self._detectionConfig['device-bi-order']
		for platform in biKeys:
			count = 0
			for hardwareHeaderList in biKeys[platform]:
				total = len(hardwareHeaderList)
				for item in hardwareHeaderList:
					if item in headers:
						count += 1
					if count == total:
						return platform

		return None

	def getMatch(self, header, value, subtree, actualHeader, category):
		f = 0
		r = 0
		treetag = header + subtree

		#print 'Get Match on branch ' + treetag
		if category is 'device':
			value = self.cleanStr(value)
		else:
			value = self.extraCleanStr(value)

		if value is "" or len(value) < 4:
			return None

		branch = self.getBranch(treetag)
		if branch is None:
			#print 'Branch is not available'
			return None

		if header == 'user-agent':
			for orderKey in branch:
				for filterKey in branch[orderKey]:
					f += 1
					if value.find(filterKey) > -1:
						for matchKey in branch[orderKey][filterKey]:
							r += 1
							if value.find(matchKey) > -1:
								self._detectedRuleKey[category] = self.cleanStr(header) + ':' + self.cleanStr(filterKey) + ':' + self.cleanStr(matchKey)
								#print 'Got Rule Key ' + category + ' ' + orderKey + ' ' + header + ' ' + filterKey + ' ' + matchKey
								#print self._detectedRuleKey
								return branch[orderKey][filterKey][matchKey]
		else:
			if value in branch:
				#print 'branch has key ' + value
				#print 'node is ' + branch[value]
				return branch[value]

		#print 'get match fails ' + category
		return None

	def getBranch(self, branchKey):
		if branchKey in self._tree:
			return self._tree[branchKey]
		
		branch = self._Store.read(branchKey)

		if branch is not None:
			self._tree[branchKey] = branch
			return branch
		return {}
