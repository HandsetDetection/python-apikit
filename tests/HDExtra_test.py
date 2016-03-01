"""Handset Detection v4 API HDExtra tests"""
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
from handsetdetection.HDExtra import *

class HDExtraTests(unittest.TestCase):

	def setUp(self):
		self.Extra = HDExtra()

	def test_comparePlatformVersionsA(self):
		result = self.Extra.comparePlatformVersions('9.0.1', '9.1')
		self.assertLessEqual(result, -1)

	def test_comparePlatformVersionsB(self):
		result = self.Extra.comparePlatformVersions('9.0.1', '9.0.1')
		self.assertEqual(result, 0)

	def test_comparePlatformVersionsC(self):
		result = self.Extra.comparePlatformVersions('9.1', '9.0.1')
		self.assertGreaterEqual(result, result)

	def test_comparePlatformVersionsD(self):
		result = self.Extra.comparePlatformVersions('4.2.1', '9.1')
		self.assertLessEqual(result, -1)

	def test_comparePlatformVersionsD2(self):
		result = self.Extra.comparePlatformVersions('4.2.1', '9')
		self.assertLessEqual(result, -1)

	def test_comparePlatformVersionsD3(self):
		result = self.Extra.comparePlatformVersions('4', '9.1.1')
		self.assertLessEqual(result, -1)

	def test_comparePlatformVersionsE(self):
		result = self.Extra.comparePlatformVersions('4.2.1', '4.2.2')
		self.assertLessEqual(result, -1)

	def test_comparePlatformVersionsF(self):
		result = self.Extra.comparePlatformVersions('4.2.1', '4.2.12')
		self.assertLessEqual(result, -1)

	def test_comparePlatformVersionsG(self):
		result = self.Extra.comparePlatformVersions('4.1.1', '4.2.1')
		self.assertLessEqual(result, -1)

	def test_comparePlatformVersionsH(self):
		result = self.Extra.comparePlatformVersions('4.1', '4.1.1')
		self.assertLessEqual(result, -1)

	def test_comparePlatformVersionsI(self):
		result = self.Extra.comparePlatformVersions('4.0.21', '40.21')
		self.assertLessEqual(result, -1)

	def test_comparePlatformVersionsJ(self):
		result = self.Extra.comparePlatformVersions('4.0.21', '10.00.1')
		self.assertLessEqual(result, -1)

	def test_comparePlatformVersionsK(self):
		result = self.Extra.comparePlatformVersions('4.0.21', '10.00.1')
		self.assertLessEqual(result, -1)

	def test_comparePlatformVersionsK2(self):
		result = self.Extra.comparePlatformVersions('10.00.1', '4')
		self.assertGreaterEqual(result, 1)

	def test_comparePlatformVersionsL(self):
		result = self.Extra.comparePlatformVersions('Q7.1', 'Q7.2')
		self.assertLessEqual(result, -1)

	def test_comparePlatformVersionsM(self):
		result = self.Extra.comparePlatformVersions('Q5SK', 'Q7SK')
		self.assertLessEqual(result, -1)


if "__main__" == __name__:
    unittest.main()