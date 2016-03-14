"""Handset Detection API implementation

The HandsetDetection class provides easy access to the Handset Detections HTTP
API version 4.
"""
# Copyright (c) 2009-2016 Teleport Corp Pty Ltd.
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
import re
import time

handsetdetection = testutils.importModule("handsetdetection")
import handsetdetection.exceptions as exceptions
from handsetdetection.HD4 import *

#unittest.TestLoader.sortTestMethodsUsing = None
class TestLoader:
	sortTestMethodsUsing = None

class HD4Tests(unittest.TestCase):

	cloudConfig = 'hd4CloudConfig.yml'
	ultimateConfig = 'hd4UltimateConfig.yml'
	communityConfig = 'hd4CommunityConfig.yml'

	devices = {
		'NokiaN95': {
			'general_vendor': 'Nokia',
			'general_model': 'N95',
			'general_platform': 'Symbian',
			'general_platform_version': '9.2',
			'general_platform_version_max': '',
			'general_browser': '',
			'general_browser_version': '',
			'general_image': 'nokian95-1403496370-0.gif',
			'general_aliases': [],
			'general_app': '',
			'general_app_category': '',
			'general_app_version': '',
			'general_language': '',
			'general_eusar': '0.50',
			'general_battery': ['Li-Ion 950 mAh','BL-5F'],
			'general_type': 'Mobile',
			'general_cpu': ['Dual ARM 11','332Mhz'],
			'design_formfactor': 'Dual Slide',
			'design_dimensions': '99 x 53 x 21',
			'design_weight': '120',
			'design_antenna': 'Internal',
			'design_keyboard': 'Numeric',
			'design_softkeys': '2',
			'design_sidekeys': ['Volume','Camera'],
			'display_type': 'TFT',
			'display_color': 'Yes',
			'display_colors': '16M',
			'display_size': '2.6"',
			'display_x': '240',
			'display_y': '320',
			'display_other': [],
			'display_pixel_ratio': '1.0',
			'display_ppi': 154,
			'memory_internal': ['160MB','64MB RAM','256MB ROM'],
			'memory_slot': ['microSD', '8GB', '128MB'],
			'network': ['GSM850','GSM900','GSM1800','GSM1900','UMTS2100','HSDPA2100','Infrared','Bluetooth 2.0','802.11b','802.11g','GPRS Class 10','EDGE Class 32'],
			'media_camera': ['5MP','2592x1944'],
			'media_secondcamera': ['QVGA'],
			'media_videocapture': ['VGA@30fps'],
			'media_videoplayback': ['MPEG4','H.263','H.264','3GPP','RealVideo 8','RealVideo 9','RealVideo 10'],
			'media_audio': ['MP3','AAC','AAC+','eAAC+','WMA'],
			'media_other': ['Auto focus','Video stabilizer','Video calling','Carl Zeiss optics','LED Flash'],
			'features': [
							  'Unlimited entries','Multiple numbers per contact','Picture ID','Ring ID','Calendar','Alarm','To-Do','Document viewer',
							  'Calculator','Notes','UPnP','Computer sync','VoIP','Music ringtones (MP3)','Vibration','Phone profiles','Speakerphone',
							  'Accelerometer','Voice dialing','Voice commands','Voice recording','Push-to-Talk','SMS','MMS','Email','Instant Messaging',
					'Stereo FM radio','Visual radio','Dual slide design','Organizer','Word viewer','Excel viewer','PowerPoint viewer','PDF viewer',
					'Predictive text input','Push to talk','Voice memo','Games'
						],
			'connectors': ['USB','miniUSB','3.5mm AUdio','TV Out'],
			'benchmark_max': 0,
			'benchmark_min': 0
		}
	}

	@classmethod
	def setUpClass(cls):
		root = os.path.dirname(os.path.dirname(__file__))
		cls.cloudConfig = os.path.join(root, cls.cloudConfig)
		cls.ultimateConfig = os.path.join(root, cls.ultimateConfig)
		cls.communityConfig = os.path.join(root, cls.communityConfig)
		
	@classmethod
	def tearDownClass(cls):
		pass

	def test_cloudDeviceVendors(self):
		hd = HandsetDetection(self.cloudConfig)
		result = hd.deviceVendors()
		reply = hd.getReply()
		
		self.assertTrue(reply)
		self.assertEquals(reply['status'], 0)
		self.assertIn('Nokia', reply['vendor'])
		self.assertIn('Samsung', reply['vendor'])

	def test_cloudDeviceModels(self):
		hd = HandsetDetection(self.cloudConfig)
		result = hd.deviceModels('Nokia')
		reply = hd.getReply()

		self.assertTrue(reply)
		self.assertEquals(reply['status'], 0)
		self.assertIn('N95', reply['model'])
		self.assertIn('N96', reply['model'])
		
	def test_cloudDeviceView(self):
		hd = HandsetDetection(self.cloudConfig)
		result = hd.deviceView('Nokia','N95')
		reply = hd.getReply()

		self.assertTrue(reply)
		self.assertEquals(reply['status'], 0)
		self.assertIn('N95', reply['device']['general_model'])
		self.assertIn('Nokia', reply['device']['general_vendor'])

	def test_cloudDeviceWhatHas(self):
		hd = HandsetDetection(self.cloudConfig)
		result = hd.deviceWhatHas('design_dimensions','101 x 44 x 16')
		reply = hd.getReply()

		self.assertTrue(reply)
		self.assertEquals(reply['status'], 0)
		self.assertIn('Asus', hd.getRawReply())
		self.assertIn('V80', hd.getRawReply())
		self.assertIn('Spice', hd.getRawReply())
		self.assertIn('S900', hd.getRawReply())

	def test_cloudDetectHTTPDesktop(self):
		""" Detection test Windows PC running Chrome """
		headers = {
			'User-Agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36'
		}

		hd = HandsetDetection(self.cloudConfig)
		result = hd.deviceDetect(headers)
		reply = hd.getReply()

		self.assertTrue(reply)
		self.assertEquals(reply['status'], 0)
		self.assertEquals(reply['message'], 'OK')
		self.assertEquals(reply['hd_specs']['general_type'], 'Computer')
		

	def test_cloudDetectHTTPDesktopJunk(self):
		""" Detection test Windows PC running Chrome """
		headers = {
			'User-Agent': 'aksjakdjkjdaiwdidjkjdkawjdijwidawjdiajwdkawdjiwjdiawjdwidjwakdjajdkad' + str(time.time())
		}

		hd = HandsetDetection(self.cloudConfig)
		result = hd.deviceDetect(headers)
		reply = hd.getReply()

		self.assertTrue(reply)
		self.assertEquals(reply['status'], 301)
		self.assertEquals(reply['message'], 'Not Found')


	def test_cloudDetectHTTPWii(self):
		""" Detection test Nintendo Wii """
		headers = {
			'User-Agent': 'Opera/9.30 (Nintendo Wii; U; ; 2047-7; es-Es)'
		}

		hd = HandsetDetection(self.cloudConfig)
		result = hd.deviceDetect(headers)
		reply = hd.getReply()

		self.assertTrue(reply)
		self.assertEquals(reply['status'], 0)
		self.assertEquals(reply['message'], 'OK')
		self.assertEquals(reply['hd_specs']['general_type'], 'Console')


	def test_cloudDetectHTTPiPhone(self):
		""" Detection test Apple iPhone """
		headers = {
			'User-Agent': 'Mozilla/5.0 (iPhone; U; CPU iPhone OS 4_3 like Mac OS X; en-gb) AppleWebKit/533.17.9 (KHTML, like Gecko)'
		}

		hd = HandsetDetection(self.cloudConfig)
		result = hd.deviceDetect(headers)
		reply = hd.getReply()

		self.assertTrue(reply)
		self.assertEquals(reply['status'], 0)
		self.assertEquals(reply['message'], 'OK')
		self.assertEquals(reply['hd_specs']['general_type'], 'Mobile')
		self.assertEquals(reply['hd_specs']['general_vendor'], 'Apple')
		self.assertEquals(reply['hd_specs']['general_model'], 'iPhone')
		self.assertEquals(reply['hd_specs']['general_platform'], 'iOS')
		self.assertEquals(reply['hd_specs']['general_platform_version'], '4.3')
		self.assertEquals(reply['hd_specs']['general_language'], 'en-gb')
		self.assertTrue(reply['hd_specs'].has_key('display_pixel_ratio'))
		self.assertTrue(reply['hd_specs'].has_key('display_ppi'))
		self.assertTrue(reply['hd_specs'].has_key('benchmark_min'))
		self.assertTrue(reply['hd_specs'].has_key('benchmark_max'))

	def test_cloudDetectHTTPiPhoneWierdHeaders(self):
		""" Detection test Apple iPhone user-agent in weird headers """
		headers = {
			'User-Agent': 'blahblahblah',
			'x-fish-header': 'Mozilla/5.0 (iPhone; U; CPU iPhone OS 4_3 like Mac OS X; en-gb) AppleWebKit/533.17.9 (KHTML, like Gecko)'
		}

		hd = HandsetDetection(self.cloudConfig)
		result = hd.deviceDetect(headers)
		reply = hd.getReply()

		self.assertTrue(reply)
		self.assertEquals(reply['status'], 0)
		self.assertEquals(reply['message'], 'OK')
		self.assertEquals(reply['hd_specs']['general_type'], 'Mobile')
		self.assertEquals(reply['hd_specs']['general_vendor'], 'Apple')
		self.assertEquals(reply['hd_specs']['general_model'], 'iPhone')
		self.assertEquals(reply['hd_specs']['general_platform'], 'iOS')
		self.assertEquals(reply['hd_specs']['general_platform_version'], '4.3')
		self.assertEquals(reply['hd_specs']['general_language'], 'en-gb')
		self.assertTrue(reply['hd_specs'].has_key('display_pixel_ratio'))
		self.assertTrue(reply['hd_specs'].has_key('display_ppi'))
		self.assertTrue(reply['hd_specs'].has_key('benchmark_min'))
		self.assertTrue(reply['hd_specs'].has_key('benchmark_max'))


	def test_cloudDetectHTTPiPhone3gs(self):
		""" Detection test iPhone 3GS (same UA as iPhone 3G, different x-local-hardwareinfo header) """
		headers = {
			'User-Agent': 'Mozilla/5.0 (iPhone; U; CPU iPhone OS 4_2_1 like Mac OS X; en-gb) AppleWebKit/533.17.9 (KHTML, like Gecko)',
			'x-local-hardwareinfo': '320:480:100:100'
		}

		hd = HandsetDetection(self.cloudConfig)
		result = hd.deviceDetect(headers)
		reply = hd.getReply()

		self.assertTrue(reply)
		self.assertEquals(reply['status'], 0)
		self.assertEquals(reply['message'], 'OK')
		self.assertEquals(reply['hd_specs']['general_type'], 'Mobile')
		self.assertEquals(reply['hd_specs']['general_vendor'], 'Apple')
		self.assertEquals(reply['hd_specs']['general_model'], 'iPhone 3GS')
		self.assertEquals(reply['hd_specs']['general_platform'], 'iOS')
		self.assertEquals(reply['hd_specs']['general_platform_version'], '4.2.1')
		self.assertEquals(reply['hd_specs']['general_language'], 'en-gb')
		self.assertEquals(reply['hd_specs']['display_pixel_ratio'],'1.0')
		self.assertEquals(reply['hd_specs']['display_ppi'], 162)

	def test_cloudDetectHTTPiPhone3g(self):
		""" Detection test iPhone 3GS (same UA as iPhone 3GS, different x-local-hardwareinfo header) """
		headers = {
			'User-Agent': 'Mozilla/5.0 (iPhone; U; CPU iPhone OS 4_2_1 like Mac OS X; en-gb) AppleWebKit/533.17.9 (KHTML, like Gecko)',
			'x-local-hardwareinfo': '320:480:100:72'
		}

		hd = HandsetDetection(self.cloudConfig)
		result = hd.deviceDetect(headers)
		reply = hd.getReply()

		self.assertTrue(reply)
		self.assertEquals(reply['status'], 0)
		self.assertEquals(reply['message'], 'OK')
		self.assertEquals(reply['hd_specs']['general_type'], 'Mobile')
		self.assertEquals(reply['hd_specs']['general_vendor'], 'Apple')
		self.assertEquals(reply['hd_specs']['general_model'], 'iPhone 3G')
		self.assertEquals(reply['hd_specs']['general_platform'], 'iOS')
		self.assertEquals(reply['hd_specs']['general_platform_version'], '4.2.1')
		self.assertEquals(reply['hd_specs']['general_language'], 'en-gb')
		self.assertEquals(reply['hd_specs']['display_pixel_ratio'],'1.0')
		self.assertEquals(reply['hd_specs']['display_ppi'], 162)


	def test_cloudDetectHTTPiPhoneCrazyBenchmark(self):
		""" Detection test iPhone - Crazy benchmark (eg from emulated desktop) with outdated OS """
		headers = {
			'User-Agent': 'Mozilla/5.0 (iPhone; U; CPU iPhone OS 2_0 like Mac OS X; en-gb) AppleWebKit/533.17.9 (KHTML, like Gecko)',
			'x-local-hardwareinfo': '320:480:200:1200'
		}

		hd = HandsetDetection(self.cloudConfig)
		result = hd.deviceDetect(headers)
		reply = hd.getReply()

		self.assertTrue(reply)
		self.assertEquals(reply['status'], 0)
		self.assertEquals(reply['message'], 'OK')
		self.assertEquals(reply['hd_specs']['general_type'], 'Mobile')
		self.assertEquals(reply['hd_specs']['general_vendor'], 'Apple')
		self.assertEquals(reply['hd_specs']['general_model'], 'iPhone 3G')
		self.assertEquals(reply['hd_specs']['general_platform'], 'iOS')
		self.assertEquals(reply['hd_specs']['general_platform_version'], '2.0')
		self.assertEquals(reply['hd_specs']['general_language'], 'en-gb')
		self.assertEquals(reply['hd_specs']['display_pixel_ratio'],'1.0')
		self.assertEquals(reply['hd_specs']['display_ppi'],162)

	def test_cloudDetectHTTPiPhone5sFacebook(self):
		""" Detection test iPhone 5s running Facebook 9.0 app (hence no general_browser set). """
		headers = {
			'user-agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 7_1_1 like Mac OS X) AppleWebKit/537.51.2 (KHTML, like Gecko) Mobile/11D201 [FBAN/FBIOS;FBAV/9.0.0.25.31;FBBV/2102024;FBDV/iPhone6,2;FBMD/iPhone;FBSN/iPhone OS;FBSV/7.1.1;FBSS/2; FBCR/vodafoneIE;FBID/phone;FBLC/en_US;FBOP/5]',
			'Accept-Language': 'da, en-gb;q=0.8, en;q=0.7'
		}

		hd = HandsetDetection(self.cloudConfig)
		result = hd.deviceDetect(headers)
		reply = hd.getReply()

		self.assertTrue(reply)
		self.assertEquals(reply['status'], 0)
		self.assertEquals(reply['message'], 'OK')
		self.assertEquals(reply['hd_specs']['general_type'], 'Mobile')
		self.assertEquals(reply['hd_specs']['general_vendor'], 'Apple')
		self.assertEquals(reply['hd_specs']['general_model'], 'iPhone 5S')
		self.assertEquals(reply['hd_specs']['general_platform'], 'iOS')
		self.assertEquals(reply['hd_specs']['general_platform_version'], '7.1.1')
		self.assertEquals(reply['hd_specs']['general_browser'], '')
		self.assertEquals(reply['hd_specs']['general_browser_version'], '')
		self.assertEquals(reply['hd_specs']['general_app'], 'Facebook')
		self.assertEquals(reply['hd_specs']['general_app_version'], '9.0')
		self.assertEquals(reply['hd_specs']['general_language'], 'da')
		self.assertEquals(reply['hd_specs']['display_pixel_ratio'],'2.0')
		self.assertEquals(reply['hd_specs']['display_ppi'], 326)


	def test_cloudDetectBIAndroid(self):
		""" Detection test Samsung GT-I9500 Native - Note : Device shipped with Android 4.2.2, so this device has been updated. """
		buildInfo = {
			'ro.build.PDA': 'I9500XXUFNE7',
			'ro.build.changelist': '699287',
			'ro.build.characteristics': 'phone',
			'ro.build.date.utc': '1401287026',
			'ro.build.date': 'Wed May 28 23:23:46 KST 2014',
			'ro.build.description': 'ja3gxx-user 4.4.2 KOT49H I9500XXUFNE7 release-keys',
			'ro.build.display.id': 'KOT49H.I9500XXUFNE7',
			'ro.build.fingerprint': 'samsung/ja3gxx/ja3g:4.4.2/KOT49H/I9500XXUFNE7:user/release-keys',
			'ro.build.hidden_ver': 'I9500XXUFNE7',
			'ro.build.host': 'SWDD5723',
			'ro.build.id': 'KOT49H',
			'ro.build.product': 'ja3g',
			'ro.build.tags': 'release-keys',
			'ro.build.type': 'user',
			'ro.build.user': 'dpi',
			'ro.build.version.codename': 'REL',
			'ro.build.version.incremental': 'I9500XXUFNE7',
			'ro.build.version.release': '4.4.2',
			'ro.build.version.sdk': '19',
			'ro.product.board': 'universal5410',
			'ro.product.brand': 'samsung',
			'ro.product.cpu.abi2': 'armeabi',
			'ro.product.cpu.abi': 'armeabi-v7a',
			'ro.product.device': 'ja3g',
			'ro.product.locale.language': 'en',
			'ro.product.locale.region': 'GB',
			'ro.product.manufacturer': 'samsung',
			'ro.product.model': 'GT-I9500',
			'ro.product.name': 'ja3gxx',
			'ro.product_ship': 'true'
		}

		hd = HandsetDetection(self.cloudConfig)
		result = hd.deviceDetect(buildInfo)
		reply = hd.getReply()

		self.assertTrue(reply)
		self.assertEquals(reply['status'], 0)
		self.assertEquals(reply['message'], 'OK')
		self.assertEquals(reply['hd_specs']['general_type'], 'Mobile')
		self.assertEquals(reply['hd_specs']['general_vendor'], 'Samsung')
		self.assertEquals(reply['hd_specs']['general_model'], 'GT-I9500')
		self.assertEquals(reply['hd_specs']['general_platform'], 'Android')
#		self.assertEquals(reply['hd_specs']['general_platform_version'], '4.4.2')


	def test_cloudDetectBiiPhone4s(self):
		buildInfo = {
			'utsname.machine': 'iphone4,1',
			'utsname.brand': 'Apple'
		}

		hd = HandsetDetection(self.cloudConfig)
		result = hd.deviceDetect(buildInfo)
		reply = hd.getReply()

		self.assertTrue(reply)
		self.assertEquals(reply['status'], 0)
		self.assertEquals(reply['message'], 'OK')
		self.assertEquals(reply['hd_specs']['general_type'], 'Mobile')
		self.assertEquals(reply['hd_specs']['general_vendor'], 'Apple')
		self.assertEquals(reply['hd_specs']['general_model'], 'iPhone 4S')
		self.assertEquals(reply['hd_specs']['general_platform'], 'iOS')
#		self.assertEquals(reply['hd_specs']['general_platform_version'], '5.0')

	def test_cloudDetectBiWindowsPhone(self):
		buildInfo = {
			'devicemanufacturer': 'nokia',
			'devicename': 'RM-875'
		}

		hd = HandsetDetection(self.cloudConfig)
		result = hd.deviceDetect(buildInfo)
		reply = hd.getReply()

		self.assertTrue(reply)
		self.assertEquals(reply['status'], 0)
		self.assertEquals(reply['message'], 'OK')
		self.assertEquals(reply['hd_specs']['general_type'], 'Mobile')
		self.assertEquals(reply['hd_specs']['general_vendor'], 'Nokia')
		self.assertEquals(reply['hd_specs']['general_model'], 'Lumia 1020')
		self.assertEquals(reply['hd_specs']['general_platform'], 'Windows Phone')

	# Ultimate Detection Tests
	def test_deviceFetchArchive(self):
		hd = HandsetDetection(self.ultimateConfig)
		hd.deviceFetchArchive()

		self.assertTrue(os.path.isfile('/tmp/ultimate-full.zip'))
		self.assertTrue(os.path.isfile('/tmp/hd40store/user-agent0.json'))

	def test_ultimateDeviceVendors(self):
		hd = HandsetDetection(self.ultimateConfig)
		result = hd.deviceVendors()
		reply = hd.getReply()
		
		self.assertTrue(reply)
		self.assertEquals(reply['status'], 0)
		self.assertIn('Nokia', reply['vendor'])
		self.assertIn('Samsung', reply['vendor'])

	def test_ultimateDeviceModels(self):
		hd = HandsetDetection(self.ultimateConfig)
		result = hd.deviceModels('Nokia')
		reply = hd.getReply()

		self.assertTrue(reply)
		self.assertEquals(reply['status'], 0)
		self.assertIn('N95', reply['model'])
		self.assertIn('N96', reply['model'])

	def test_ultimateDeviceView(self):
		hd = HandsetDetection(self.ultimateConfig)
		result = hd.deviceView('Nokia','N95')
		reply = hd.getReply()

		self.assertTrue(reply)
		self.assertEquals(reply['status'], 0)
		self.assertIn('N95', reply['device']['general_model'])
		self.assertIn('Nokia', reply['device']['general_vendor'])

	def test_ultimateDeviceWhatHas(self):
		hd = HandsetDetection(self.ultimateConfig)
		result = hd.deviceWhatHas('design_dimensions','101 x 44 x 16')
		reply = hd.getReply()

		self.assertTrue(reply)
		self.assertEquals(reply['status'], 0)
		self.assertIn('Asus', hd.getRawReply())
		self.assertIn('V80', hd.getRawReply())
		self.assertIn('Spice', hd.getRawReply())
		self.assertIn('S900', hd.getRawReply())

	def test_ultimateDetectHTTPDesktop(self):
		""" Detection test Windows PC running Chrome """
		headers = {
			'User-Agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36'
		}

		hd = HandsetDetection(self.ultimateConfig)
		result = hd.deviceDetect(headers)
		reply = hd.getReply()

		self.assertTrue(reply)
		self.assertEquals(reply['status'], 0)
		self.assertEquals(reply['message'], 'OK')
		self.assertEquals(reply['hd_specs']['general_type'], 'Computer')


	def test_ultimateDetectHTTPDesktopJunk(self):
		""" Detection test Windows PC running Chrome """
		headers = {
			'User-Agent': 'aksjakdjkjdaiwdidjkjdkawjdijwidawjdiajwdkawdjiwjdiawjdwidjwakdjajdkad' + str(time.time())
		}

		hd = HandsetDetection(self.ultimateConfig)
		result = hd.deviceDetect(headers)
		reply = hd.getReply()

		self.assertTrue(reply)
		self.assertEquals(reply['status'], 301)
		self.assertEquals(reply['message'], 'Not Found')


	def test_ultimateDetectHTTPWii(self):
		""" Detection test Nintendo Wii """
		headers = {
			'User-Agent': 'Opera/9.30 (Nintendo Wii; U; ; 2047-7; es-Es)'
		}

		hd = HandsetDetection(self.ultimateConfig)
		result = hd.deviceDetect(headers)
		reply = hd.getReply()

		self.assertTrue(reply)
		self.assertEquals(reply['status'], 0)
		self.assertEquals(reply['message'], 'OK')
		self.assertEquals(reply['hd_specs']['general_type'], 'Console')


	def test_ultimateDetectHTTPiPhone(self):
		""" Detection test Apple iPhone """
		headers = {
			'User-Agent': 'Mozilla/5.0 (iPhone; U; CPU iPhone OS 4_3 like Mac OS X; en-gb) AppleWebKit/533.17.9 (KHTML, like Gecko)'
		}

		hd = HandsetDetection(self.ultimateConfig)
		result = hd.deviceDetect(headers)
		reply = hd.getReply()

		self.assertTrue(reply)
		self.assertEquals(reply['status'], 0)
		self.assertEquals(reply['message'], 'OK')
		self.assertEquals(reply['hd_specs']['general_type'], 'Mobile')
		self.assertEquals(reply['hd_specs']['general_vendor'], 'Apple')
		self.assertEquals(reply['hd_specs']['general_model'], 'iPhone')
		self.assertEquals(reply['hd_specs']['general_platform'], 'iOS')
		self.assertEquals(reply['hd_specs']['general_platform_version'], '4.3')
		self.assertEquals(reply['hd_specs']['general_language'], 'en-gb')
		self.assertTrue(reply['hd_specs'].has_key('display_pixel_ratio'))
		self.assertTrue(reply['hd_specs'].has_key('display_ppi'))
		self.assertTrue(reply['hd_specs'].has_key('benchmark_min'))
		self.assertTrue(reply['hd_specs'].has_key('benchmark_max'))

	def test_ultimateDetectHTTPiPhoneWierdHeaders(self):
		""" Detection test Apple iPhone user-agent in weird headers """
		headers = {
			'User-Agent': 'blahblahblah',
			'x-fish-header': 'Mozilla/5.0 (iPhone; U; CPU iPhone OS 4_3 like Mac OS X; en-gb) AppleWebKit/533.17.9 (KHTML, like Gecko)'
		}

		hd = HandsetDetection(self.ultimateConfig)
		result = hd.deviceDetect(headers)
		reply = hd.getReply()

		self.assertTrue(reply)
		self.assertEquals(reply['status'], 0)
		self.assertEquals(reply['message'], 'OK')
		self.assertEquals(reply['hd_specs']['general_type'], 'Mobile')
		self.assertEquals(reply['hd_specs']['general_vendor'], 'Apple')
		self.assertEquals(reply['hd_specs']['general_model'], 'iPhone')
		self.assertEquals(reply['hd_specs']['general_platform'], 'iOS')
		self.assertEquals(reply['hd_specs']['general_platform_version'], '4.3')
		self.assertEquals(reply['hd_specs']['general_language'], 'en-gb')
		self.assertTrue(reply['hd_specs'].has_key('display_pixel_ratio'))
		self.assertTrue(reply['hd_specs'].has_key('display_ppi'))
		self.assertTrue(reply['hd_specs'].has_key('benchmark_min'))
		self.assertTrue(reply['hd_specs'].has_key('benchmark_max'))


	def test_ultimateDetectHTTPiPhone3gs(self):
		""" Detection test iPhone 3GS (same UA as iPhone 3G, different x-local-hardwareinfo header) """
		headers = {
			'User-Agent': 'Mozilla/5.0 (iPhone; U; CPU iPhone OS 4_2_1 like Mac OS X; en-gb) AppleWebKit/533.17.9 (KHTML, like Gecko)',
			'x-local-hardwareinfo': '320:480:100:100'
		}

		hd = HandsetDetection(self.ultimateConfig)
		result = hd.deviceDetect(headers)
		reply = hd.getReply()

		self.assertTrue(reply)
		self.assertEquals(reply['status'], 0)
		self.assertEquals(reply['message'], 'OK')
		self.assertEquals(reply['hd_specs']['general_type'], 'Mobile')
		self.assertEquals(reply['hd_specs']['general_vendor'], 'Apple')
		self.assertEquals(reply['hd_specs']['general_model'], 'iPhone 3GS')
		self.assertEquals(reply['hd_specs']['general_platform'], 'iOS')
		self.assertEquals(reply['hd_specs']['general_platform_version'], '4.2.1')
		self.assertEquals(reply['hd_specs']['general_language'], 'en-gb')
		self.assertEquals(reply['hd_specs']['display_pixel_ratio'],'1.0')
		self.assertEquals(reply['hd_specs']['display_ppi'], 162)

	def test_ultimateDetectHTTPiPhone3g(self):
		""" Detection test iPhone 3GS (same UA as iPhone 3GS, different x-local-hardwareinfo header) """
		headers = {
			'User-Agent': 'Mozilla/5.0 (iPhone; U; CPU iPhone OS 4_2_1 like Mac OS X; en-gb) AppleWebKit/533.17.9 (KHTML, like Gecko)',
			'x-local-hardwareinfo': '320:480:100:72'
		}

		hd = HandsetDetection(self.ultimateConfig)
		result = hd.deviceDetect(headers)
		reply = hd.getReply()

		self.assertTrue(reply)
		self.assertEquals(reply['status'], 0)
		self.assertEquals(reply['message'], 'OK')
		self.assertEquals(reply['hd_specs']['general_type'], 'Mobile')
		self.assertEquals(reply['hd_specs']['general_vendor'], 'Apple')
		self.assertEquals(reply['hd_specs']['general_model'], 'iPhone 3G')
		self.assertEquals(reply['hd_specs']['general_platform'], 'iOS')
		self.assertEquals(reply['hd_specs']['general_platform_version'], '4.2.1')
		self.assertEquals(reply['hd_specs']['general_language'], 'en-gb')
		self.assertEquals(reply['hd_specs']['display_pixel_ratio'],'1.0')
		self.assertEquals(reply['hd_specs']['display_ppi'], 162)


	def test_ultimateDetectHTTPiPhoneCrazyBenchmark(self):
		""" Detection test iPhone - Crazy benchmark (eg from emulated desktop) with outdated OS """
		headers = {
			'User-Agent': 'Mozilla/5.0 (iPhone; U; CPU iPhone OS 2_0 like Mac OS X; en-gb) AppleWebKit/533.17.9 (KHTML, like Gecko)',
			'x-local-hardwareinfo': '320:480:200:1200'
		}

		hd = HandsetDetection(self.ultimateConfig)
		result = hd.deviceDetect(headers)
		reply = hd.getReply()

		self.assertTrue(reply)
		self.assertEquals(reply['status'], 0)
		self.assertEquals(reply['message'], 'OK')
		self.assertEquals(reply['hd_specs']['general_type'], 'Mobile')
		self.assertEquals(reply['hd_specs']['general_vendor'], 'Apple')
		self.assertEquals(reply['hd_specs']['general_model'], 'iPhone 3G')
		self.assertEquals(reply['hd_specs']['general_platform'], 'iOS')
		self.assertEquals(reply['hd_specs']['general_platform_version'], '2.0')
		self.assertEquals(reply['hd_specs']['general_language'], 'en-gb')
		self.assertEquals(reply['hd_specs']['display_pixel_ratio'],'1.0')
		self.assertEquals(reply['hd_specs']['display_ppi'],162)

	def test_ultimateDetectHTTPiPhone5sFacebook(self):
		""" Detection test iPhone 5s running Facebook 9.0 app (hence no general_browser set). """
		headers = {
			'user-agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 7_1_1 like Mac OS X) AppleWebKit/537.51.2 (KHTML, like Gecko) Mobile/11D201 [FBAN/FBIOS;FBAV/9.0.0.25.31;FBBV/2102024;FBDV/iPhone6,2;FBMD/iPhone;FBSN/iPhone OS;FBSV/7.1.1;FBSS/2; FBCR/vodafoneIE;FBID/phone;FBLC/en_US;FBOP/5]',
			'Accept-Language': 'da, en-gb;q=0.8, en;q=0.7'
		}

		hd = HandsetDetection(self.ultimateConfig)
		result = hd.deviceDetect(headers)
		reply = hd.getReply()

		self.assertTrue(reply)
		self.assertEquals(reply['status'], 0)
		self.assertEquals(reply['message'], 'OK')
		self.assertEquals(reply['hd_specs']['general_type'], 'Mobile')
		self.assertEquals(reply['hd_specs']['general_vendor'], 'Apple')
		self.assertEquals(reply['hd_specs']['general_model'], 'iPhone 5S')
		self.assertEquals(reply['hd_specs']['general_platform'], 'iOS')
		self.assertEquals(reply['hd_specs']['general_platform_version'], '7.1.1')
		self.assertEquals(reply['hd_specs']['general_browser'], '')
		self.assertEquals(reply['hd_specs']['general_browser_version'], '')
		self.assertEquals(reply['hd_specs']['general_app'], 'Facebook')
		self.assertEquals(reply['hd_specs']['general_app_version'], '9.0')
		self.assertEquals(reply['hd_specs']['general_language'], 'da')
		self.assertEquals(reply['hd_specs']['display_pixel_ratio'],'2.0')
		self.assertEquals(reply['hd_specs']['display_ppi'], 326)


	def test_ultimateDetectBIAndroid(self):
		""" Detection test Samsung GT-I9500 Native - Note : Device shipped with Android 4.2.2, so this device has been updated. """
		buildInfo = {
			'ro.build.PDA': 'I9500XXUFNE7',
			'ro.build.changelist': '699287',
			'ro.build.characteristics': 'phone',
			'ro.build.date.utc': '1401287026',
			'ro.build.date': 'Wed May 28 23:23:46 KST 2014',
			'ro.build.description': 'ja3gxx-user 4.4.2 KOT49H I9500XXUFNE7 release-keys',
			'ro.build.display.id': 'KOT49H.I9500XXUFNE7',
			'ro.build.fingerprint': 'samsung/ja3gxx/ja3g:4.4.2/KOT49H/I9500XXUFNE7:user/release-keys',
			'ro.build.hidden_ver': 'I9500XXUFNE7',
			'ro.build.host': 'SWDD5723',
			'ro.build.id': 'KOT49H',
			'ro.build.product': 'ja3g',
			'ro.build.tags': 'release-keys',
			'ro.build.type': 'user',
			'ro.build.user': 'dpi',
			'ro.build.version.codename': 'REL',
			'ro.build.version.incremental': 'I9500XXUFNE7',
			'ro.build.version.release': '4.4.2',
			'ro.build.version.sdk': '19',
			'ro.product.board': 'universal5410',
			'ro.product.brand': 'samsung',
			'ro.product.cpu.abi2': 'armeabi',
			'ro.product.cpu.abi': 'armeabi-v7a',
			'ro.product.device': 'ja3g',
			'ro.product.locale.language': 'en',
			'ro.product.locale.region': 'GB',
			'ro.product.manufacturer': 'samsung',
			'ro.product.model': 'GT-I9500',
			'ro.product.name': 'ja3gxx',
			'ro.product_ship': 'true'
		}

		hd = HandsetDetection(self.ultimateConfig)
		result = hd.deviceDetect(buildInfo)
		reply = hd.getReply()

		self.assertTrue(reply)
		self.assertEquals(reply['status'], 0)
		self.assertEquals(reply['message'], 'OK')
		self.assertEquals(reply['hd_specs']['general_type'], 'Mobile')
		self.assertEquals(reply['hd_specs']['general_vendor'], 'Samsung')
		self.assertEquals(reply['hd_specs']['general_model'], 'GT-I9500')
		self.assertEquals(reply['hd_specs']['general_platform'], 'Android')
#		self.assertEquals(reply['hd_specs']['general_platform_version'], '4.4.2')


	def test_ultimateDetectBiiPhone4s(self):
		buildInfo = {
			'utsname.machine': 'iphone4,1',
			'utsname.brand': 'Apple'
		}

		hd = HandsetDetection(self.ultimateConfig)
		result = hd.deviceDetect(buildInfo)
		reply = hd.getReply()

		self.assertTrue(reply)
		self.assertEquals(reply['status'], 0)
		self.assertEquals(reply['message'], 'OK')
		self.assertEquals(reply['hd_specs']['general_type'], 'Mobile')
		self.assertEquals(reply['hd_specs']['general_vendor'], 'Apple')
		self.assertEquals(reply['hd_specs']['general_model'], 'iPhone 4S')
		self.assertEquals(reply['hd_specs']['general_platform'], 'iOS')
#		self.assertEquals(reply['hd_specs']['general_platform_version'], '5.0')

	def test_ultimateDetectBiWindowsPhone(self):
		buildInfo = {
			'devicemanufacturer': 'nokia',
			'devicename': 'RM-875'
		}

		hd = HandsetDetection(self.ultimateConfig)
		result = hd.deviceDetect(buildInfo)
		reply = hd.getReply()

		self.assertTrue(reply)
		self.assertEquals(reply['status'], 0)
		self.assertEquals(reply['message'], 'OK')
		self.assertEquals(reply['hd_specs']['general_type'], 'Mobile')
		self.assertEquals(reply['hd_specs']['general_vendor'], 'Nokia')
		self.assertEquals(reply['hd_specs']['general_model'], 'Lumia 1020')
		self.assertEquals(reply['hd_specs']['general_platform'], 'Windows Phone')


	#Todo : ultimate tests - same as cloud tests but using ultimate config
	

	# Ultimate Community Tests
	def test_communityFetchArchive(self):
		pass
		
		
	#Todo : ultimate community tests - same as ultimate tests but some fields are empty


if "__main__" == __name__:
    unittest.main()
