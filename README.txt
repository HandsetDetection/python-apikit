HandsetDetection Python API kit
===============================

:Author: Richard Uren richard@teleport.com.au
:Copyright: 2009 - 2016 Teleport Corp Pty Ltd.
:License: see the file LICENSE

This is a Python module exposing the Handset Detection API version 4.0.  If you
aren't sure what that means, please visit http://handsetdetection.readme.io/ for
an API overview

API
---

The Handset Detection API has the following available methods:
deviceDetect, deviceVendor, deviceModel, deviceView, deviceWhatHas,
deviceFetchArchive and communityFetchArchive.

Additionally the kit cam operate in 'Cloud' mode, sending requests to
a web service, or 'Ultimate' mode, resolving requests locally.

deviceDetect(headers, options)
    Get device information from HTTP headers such as a user-agent. Note:
	you can substitute HTTP headers for native device build information and
	Handset Detection can detect based on that as well.

    headers - a dictionary containing a User-Agent, IP address, x-wap-profile,
           and any other information that may be useful in identifying the
           handset
    options - a string or list of options to be returned from your query,
              e.g., "geoip" or ["geoip", "product_info"], etc.

deviceVendors()
	Provides a list of all vendors

deviceModels(vendor)
    List all model names for a given vendor.

deviceView(vendor, model)
	Get the specs for a device gien its vendor and model

deviceWhatHas(key, value)
	List all models who's key has the requested value.

deviceFetchArchive()
	Fetches the current device archive from our servers and installs locally
	for high performance device lookups. Note : Requires a license.

communityFetchArchive()
	Fetches a free version of our device archive and installs it locally
	for high performance device lookups. Functionally this is the same
	as deviceFetchArchive however the device specs schemas are reduced to
	a much smaller working set.

Examples
--------

See the examples.py file