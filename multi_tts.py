#!/usr/bin/python3
#+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
#|R|a|s|p|b|e|r|r|y|P|i|.|c|o|m|.|t|w|
#+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
# Copyright (c) 2019, raspberrypi.com.tw
# All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.
#
# multi_tts.py
# Test TTS(Text To Speech) in CHT IoT Platform
#
# Author : sosorry
# Date   : 2019/08/07
# Usage  : python3 multi_tts.py
# https://stackoverflow.com/questions/17960942/attributeerror-module-object-has-no-attribute-urlretrieve

import sys 
import requests
import json
import os
from urllib.request import urlretrieve
import configparser 

config = configparser.ConfigParser()
config.read('cht.conf')
apiKey = config.get('demo-key', 'apiKey')
headers = {'X-API-KEY': apiKey}

inputText = '中華電信大平台發大財'

try:
    if sys.argv[1] == 'ch' and sys.argv[2] is not None:
        apiURL = 'https://iot.cht.com.tw/apis/CHTIoT/tts/v1/ch/synthesis'
        inputText = sys.argv[2]
        my_data = {'inputText': inputText, 'speaker': 'lsj', 'outputName': 'out.mp3'}
    elif sys.argv[1] == 'tw' and sys.argv[2] is not None:
        apiURL = 'https://iot.cht.com.tw/apis/CHTIoT/tts/v1/tw/synthesis'
        inputText = sys.argv[2]
        my_data = {'inputText': inputText, 'outputName': 'out.mp3'}
except:
    apiURL = 'https://iot.cht.com.tw/apis/CHTIoT/tts/v1/ch/synthesis'
    my_data = {'inputText': inputText, 'outputName': 'out.mp3'}

r = requests.post(apiURL, data = my_data)
print(r.status_code)
f = json.loads(r.text)['file']

urlretrieve(f, "out.mp3")
os.system("aplay out.mp3")

