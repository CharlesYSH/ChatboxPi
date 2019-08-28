# encoding=UTF-8
import requests
import json
import base64
import sys
import os
import configparser
import time

def add_face_to_facegroup(apiKey, GROUP_ID, imagePath, server='http://iot.cht.com.tw/apis/CHTIoT'):
    apiURL = "{}{}{}".format(server, '/face/v2/FaceGroup/', GROUP_ID)

    headers = {
        "X-API-KEY": apiKey,
        "Content-Type": "application/json",
    }

    files = {"name": open(imagePath, "rb")}
    fileName = os.path.basename(imagePath)
    imgData = base64.b64encode(files["name"].read()).decode('utf-8')

    data = {
        "imgData":imgData,
        "faceMetadata": os.path.splitext(fileName)[0]
    }

    response = requests.post(apiURL, headers = headers, data=json.dumps(data))
    print(response.text)
    return response.text

def create_face_group(apiKey, server='http://iot.cht.com.tw/apis/CHTIoT'):
    apiURL = "{}{}".format(server, '/face/v2/FaceGroup')

    headers = {
        "X-API-KEY": apiKey,
        "Content-Type": "application/json",
    }

    data = {
        "groupName":"mygroup",
        "groupMetadata":"this is my best team"
    }

    response = requests.post(apiURL, headers=headers, data=json.dumps(data))
    return response.text

def delete_face_group(apiKey, GROUP_ID, server='http://iot.cht.com.tw/apis/CHTIoT'):
    apiURL = "{}{}{}".format(server, '/face/v2/FaceGroup/', GROUP_ID)

    headers = {
        "X-API-KEY": apiKey,
        "Content-Type": "application/json",
    }

    response = requests.delete(apiURL, headers=headers)
    return response.text
    
def get_face_group(apiKey, server='http://iot.cht.com.tw/apis/CHTIoT'):
    apiURL = "{}{}".format(server, '/face/v2/FaceGroup')

    headers = {
        "X-API-KEY": apiKey,
        "Content-Type": "application/json",
    }

    response = requests.request("GET", apiURL, headers=headers)
    print(response.text)
    try:
        groupid = json.loads(response.text)['faceGroups'][0]['groupId']
        print(groupid)
        groupid = trans_num(groupid)
    except:
        groupid=None
    print(groupid)
    return groupid
    
def recognize_face_in_facegroup(apiKey, GROUP_ID, imagePath, server='http://iot.cht.com.tw/apis/CHTIoT'):
    apiURL = "{}{}{}{}".format(server, '/face/v2/FaceGroup/', GROUP_ID, '/Match')

    headers = {
        "X-API-KEY": apiKey,
        "Content-Type": "application/json",
    }

    files = {"name": open(imagePath, "rb")}
    fileName = os.path.basename(imagePath)
    imgData = base64.b64encode(files["name"].read()).decode('utf-8')

    data = {
        "queryData":imgData,
    }

    response = requests.post(apiURL, headers = headers, data=json.dumps(data))
    return response.text

def take_photo(resolution="320x240 ", folder='faceAPI/image/', photo_name='verify', type='jpg'):
    os.system("fswebcam -r "+ resolution + folder + photo_name + '.' + type)
    
def get_led_status():
    config = configparser.ConfigParser()
    config.read('faceAPI/cht2.conf')
    projectKey = config.get('device-key', 'projectKey')
    deviceId   = config.get('device-key', 'deviceId')
    statusId   = config.get('device-key', 'statusId')

    apiURL = 'http://iot.cht.com.tw/iot/v1/device/' + deviceId +'/sensor/' + statusId +'/rawdata'
    headers = { 
        "CK":projectKey,
        "Content-Type": "application/json",
    }   

    response = requests.get(apiURL, headers=headers)
    s = json.loads(response.text)['value'][0]
    return s

def set_led_status(value):
    config = configparser.ConfigParser()
    config.read('faceAPI/cht2.conf')
    projectKey = config.get('device-key', 'projectKey')
    deviceId   = config.get('device-key', 'deviceId')
    controlId   = config.get('device-key', 'controlId')

    apiURL = 'http://iot.cht.com.tw/iot/v1/device/' + deviceId + '/rawdata'
    headers = { 
        "CK":projectKey,
        "Content-Type": "application/json",
    }
    t = str(time.strftime("%Y-%m-%dT%H:%M:%S"))
    payload=[{"id":controlId, "value":[value]}]
    print(payload)	

    response = requests.post(apiURL, headers=headers, data=json.dumps(payload))
    return response.text

def get_environment(sensorID):
    projectKey = "PKFUY33G3NKQF14O7G"
    deviceID = "17598687058"
    #sensorID = "temperature"
    
    apiURL = 'http://iot.cht.com.tw/iot/v1/device/' + deviceID + '/sensor/' + sensorID + '/rawdata'
    headers = { 
        "CK":projectKey,
        "Content-Type": "application/json",
    }

    response = requests.get(apiURL, headers=headers)
    #print(response.text)
    s = json.loads(response.text)['value'][0]
    return s

def trans_num(source):
    dic_num = {"0":u"零","1":u"壹","2":u"貳","3":u"三","4":u"肆","5":u"伍","6":u"陸","7":u"柒","8":u"八","9":u"玖"}

    target = source[:2]
    for i in range(2,len(source)):
        target += dic_num[source[i]]
    return target
