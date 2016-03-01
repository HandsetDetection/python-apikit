#!/usr/bin/python
#
# Copyright (c) 2009 - 2016 Teleport Corp Pty Ltd.
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

# Note: Update the hd_config.yml file in the project root with your API credentials and site id.
from handsetdetection.HD4 import *

hd4 = HandsetDetection()

# List all vendors
vendors = hd4.deviceVendors()
print vendors

# List all models for a vendor
models = hd4.deviceModels("Nokia")
print models

# List information about a device
device = hd4.deviceView("Nokia","N95")
print device

# List all devices that have a general_type of Bot
whathas = hd4.deviceWhatHas("general_type","Bot")
print whathas

# Detect a Nokia N95
result = hd4.deviceDetect({'User-Agent':'Nokia N95', 'x-wap-profile':''}, {})
print result

# Detect a Sony X10i
result = hd4.deviceDetect({'User-Agent':'Mozilla/5.0 (Linux; U; Android 2.1-update1; cs-cz; SonyEricssonX10i Build/2.1.B.0.1) AppleWebKit/530.17 (KHTML, like Gecko) Version/4.0 Mobile Safari/530.17', 'x-wap-profile':''}, {})
print result

# Download and install an Ultimate licence
# Note: Requires use_local set to true . Above calls will fail until archive is installed.
#hd4.deviceFetchArchive()