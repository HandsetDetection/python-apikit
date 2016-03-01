"""Handset Detection API Cache Helper class
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

from dogpile.cache import make_region
from dogpile.cache.util import sha1_mangle_key
from dogpile.cache.api import NO_VALUE

hd40cache = {}

class HDCache(object):
	_keyPrefix = 'hd40'
	_capacity = 10000
	_cache = None
	_region = None
	config = {
		'cache' : {
			'backend': 'dogpile.cache.memory',
			'expiry' : 3600,
			'arguments' : { 'cache_dict' : hd40cache }
		}
	}

	def __init__(self, config = None):
		if config is not None:
			self.setConfig(config)
		else:
			self.setConfig(self.config)

	def setConfig(self, config):
		if config.has_key('cache'):
			self.config = config

			if config['cache'].has_key('backend'):
				self._backend = config['cache']['backend']
			if config['cache'].has_key('expiry'):
				self._expiry = config['cache']['expiry']
			if config['cache'].has_key('arguments'):
				self._arguments = config['cache']['arguments']

			self._region = make_region(key_mangler=sha1_mangle_key).configure(
				self._backend,
				expiration_time = self._expiry,
				arguments = self._arguments
			)

	def read(self, key):
		"""Read a key from the cache

		string - key
		"""
		data = self._region.get(key);
		if data == NO_VALUE:
			return None
		return data

	def write(self, key, data):
		"""Write data to the cache

		string - key
		object - data
		"""
		self._region.set(key, data)
		return True

	def purge(self, key):
		"""Purge key from the cache"""
		return self._region.delete(key)

