#!/usr/bin/python3
#+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
#|R|a|s|p|b|e|r|r|y|P|i|.|c|o|m|.|t|w|
#+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
# Copyright (c) 2019, raspberrypi.com.tw
# All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.
#
# add_sensor_data.py
# Add sensor data from specific sensor of CHT IoT Platform
#
# Author : sosorry
# Date   : 2019/08/07

import requests
import numpy as np
import time
import json
import configparser 

config = configparser.ConfigParser()
config.read('cht.conf')
projectKey = config.get('device-key', 'projectKey')
deviceId   = config.get('device-key', 'deviceId')
statusId   = config.get('device-key', 'statusId')

apiURL = 'http://iot.cht.com.tw/iot/v1/device/' + deviceId +'/sensor/' + statusId +'/rawdata'
headers = { 
        "CK":projectKey,
    "Content-Type": "application/json",
}   

#v = str(int(np.random.random() *100))
#t = str(time.strftime("%Y-%m-%dT%H:%M:%S"))
#payload=[{"id":sensorId, "value":[v]}]
#print(payload)

response = requests.get(apiURL, headers=headers)
s = json.loads(response.text)['value'][0]
print(s)

