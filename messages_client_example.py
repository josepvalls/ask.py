#!/usr/bin/python
import json
import subprocess
import urllib2
import hashlib
import datetime

try:
  data = subprocess.check_output(["python","/usr/local/bin/temper-poll"])
  temp = data.splitlines()[1][11:15]
  temp = "The temperature upstairs is %s" % temp
except:
  temp = "Cannot read the temperature"

dt = datetime.datetime.fromtimestamp(time.mktime(time.gmtime()))
timestamp = int((dt - datetime.datetime(1970, 1, 1)).total_seconds())
hash = hashlib.md5("%d:%s" % (timestamp,secret)).hexdigest()
sticky = timestamp + 3600
req = urllib2.Request(api, json.dumps({"text":temp,"userId":userid,"timestamp":timestamp,"hash":hash,"source":"api","sticky":sticky,"key":"temper-upstairs"}), {'Content-Type': 'application/json'})
f = urllib2.urlopen(req)
response = f.read()
f.close()