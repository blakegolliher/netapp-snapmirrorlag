#!/usr/local/python-2.7.2/bin/python

##
#
# Simple snapmirror lag report.
#
# Based on the netapp sample snapmirror.py in
# netapp-manageability-sdk-5.1/src/sample/Data_ONTAP/Python
#
# Blake Golliher - blakegolliher@gmail.com
#
##

import sys, string, os
# Make sure your netapp-manageability-sdk is unzipped, and the path put here.
sys.path.append("/var/netapp-manageability-sdk-5.1/lib/python/NetApp")
from NaServer import *
import getpass
import datetime
import time
from math import log

password = getpass.getpass()

## Thanks internet!
## http://stackoverflow.com",/questions/1094841/reusable-library-to-get-human-readable-version-of-file-size
unit_list = zip(['bytes', 'kB', 'MB', 'GB', 'TB'], [0, 0, 1, 2, 2])
def sizeof_fmt(num):
    """Human friendly file size"""
    if num > 1:
        exponent = min(int(log(num, 1024)), len(unit_list) - 1)
        quotient = float(num) / 1024**exponent
        unit, num_decimals = unit_list[exponent]
        format_string = '{:.%sf} {}' % (num_decimals)
        return format_string.format(quotient, unit)
    if num == 0:
        return '0 bytes'
    if num == 1:
        return '1 byte'

## filer_name = sys.argv[1]

filer_list = ( "filer101",
	       "filer102",
	       "filer103",
	       "filer104",
	       "filer105",
	       "filer106",
	       "filer107",
	       "filer108",
	       "filer109",
	       "filer110",
	       "filer111")

for filer_name in filer_list:
	print "============ %s ============ " % filer_name
	filer = NaServer(filer_name,1,6)
	filer.set_admin_user('root', 'password')
	cmd = NaElement("snapmirror-get-status")
	ret = filer.invoke_elem(cmd)

	if(ret.results_status() == "failed"):
		print "%s failed." % filer_name
		print(ret.results_reason() + "\n")
		sys.exit(2)
	
	status = ret.child_get("snapmirror-status")

	if(not(status == None)):
		result = status.children_get()
	else:
		print "status_children_get was empty\n"
		sys.exit(2)

for snapStat in result:
	src = snapStat.child_get_string("source-location")
	dest = snapStat.child_get_string("destination-location")
	lag = int(snapStat.child_get_string("lag-time"))
	last_time_secs = int(snapStat.child_get_string("last-transfer-duration"))
	last_xfer_size = float(snapStat.child_get_string("last-transfer-size"))
	last_mirror_ts = int(snapStat.child_get_string("mirror-timestamp"))
	status = snapStat.child_get_string("status")
	state = snapStat.child_get_string("state")
	xfer_progress = float(snapStat.child_get_string("transfer-progress"))
	print "Snapmirror Report : %s to %s has a lag of %s." % (src,dest,(time.strftime('%H:%M:%S', time.gmtime(lag))))
	print "		Snapmirror Source 		: %s" % src
	print "		Snapmirror Destination		: %s" % dest
	print "		Snapmirror Lag 	 		: %s" % time.strftime('%H:%M:%S', time.gmtime(lag))
	print "		Last Transfer Time		: %s" % time.strftime('%H:%M:%S', time.gmtime(last_time_secs))
	print "		Last Transfer Size		: %s" % sizeof_fmt(last_xfer_size)
	print "		Last Mirror Timestamp		: %s" % time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(last_mirror_ts))
	print "		Snapmirror Status		: %s" % status
	print "		Snapmirror State		: %s" % state
	print "		Snapmirror xfer Progress	: %s\n" % sizeof_fmt(xfer_progress)
