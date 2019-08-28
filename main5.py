# encoding=UTF-8
import logging
import threading
import time
import requests
from requests import Request,Session
import json
import pyaudio
from pyaudio import PyAudio
import wave

import sys 
import os
from urllib.request import urlretrieve
import configparser 
from faceAPI import faceAPI

sys.path.insert(1, './mics_hat')
import LOOK

logging.basicConfig(level=logging.DEBUG, format="%(message)s")

CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 16000
RECORD_SECONDS = 3
WAVE_OUTPUT_FILENAME = "voice.raw"

def my_record(flag):
    p = pyaudio.PyAudio()
    stream = p.open(format = FORMAT,
                channels = CHANNELS,
                rate = RATE,
                input = True,
                frames_per_buffer = CHUNK)
    frames = []
    ledc = LOOK.LEDconnect()
    
    if flag:
        print("START")
    else:
        print("Triger Success")
        #au = LOOK.AudioFile("/home/pi/Desktop/mics_hat/siri-sound-effect-hd1.wav")
        #au.play()
        #au.close()
        ledc.think()
    for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
        data = stream.read(CHUNK)
        frames.append(data)
    print("STOP")
    ledc.close()
    
        
    stream.stop_stream()
    stream.close()
    p.terminate()

    wf = wave.open(WAVE_OUTPUT_FILENAME, 'wb')
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(p.get_sample_size(FORMAT))
    wf.setframerate(RATE)
    wf.writeframes(b''.join(frames))
    wf.close()


def run():
    lens = 0
    #支援辨識pcm-16,16kHz語音
    file = open('voice.raw', 'rb')
    if not file:
        print("Not file")
        raise
    
    DataBuffer = file.read()
    lens = len(DataBuffer)
    
    gStartTime = time.time()
    gTimeToSync = 0.15
    #步驟一:設定參數
    param = {
    'Action':'connect'
    }
    
    header_API_Key = {
        'X-API-Key':'09bfe6e9-28ea-4f77-aac3-d123263145eXX4', #請自行至https://iot.cht.com.tw/iot/appkey 申請API金鑰
        'Content-type':'application/octet-stream' 
    }
    #步驟二:開始連線，因為要用http 1.1 keep-alive python必須用session
    session = requests.Session()
    
    GWurl= 'http://iot.cht.com.tw/apis/CHTIoT/chtlasr/v2/MyServlet/tlasr'
    res = session.post(GWurl, headers=header_API_Key, params=param, data="")

    #步驟三:取得ASR Reference Id, 用來告訴server這些語音buffer是同一次辨識
    res_json = json.loads(res.text)
    ResulsStatus = res_json["ResultStatus"]
    if(ResulsStatus != "Success"):
        print("ErrorMsg:"+res_json["ErrorMessage"])
    
    handle=res_json["AsrReferenceId"]


    #print('post Action:connect:(',res.text,')')
    #print('handle:(',handle,')')

    if str(res.text).find('fail') == -1: 
        j = 0
        while j < lens: #支援streaming辨識，可以邊錄邊傳，此範例將音檔以每4800 byte(0.15秒)進行傳送，以模擬邊錄邊傳，透過以下API可以將音訊即時傳至後端辨識
            bytessend = 4800 #每次傳送長度，需進行調教，來達到較佳的辨識速度，建議值為0.08秒~0.15秒之間
            if(j + bytessend > lens):
                bytessend = lens - j
                
            #步驟四:開始傳送音訊buffer，取得辨識狀態
            param = {
            'Action':'syncData',
            'AsrReferenceId':handle,
            'ByteNum':bytessend,
            'SpeechEnd':'n'
            }
            res = session.post(GWurl, headers=header_API_Key, params=param, data=DataBuffer[j:j+bytessend])
            j = j + bytessend

            #模擬streaming錄音時間，送0.15sec語音
            if(time.time()-gStartTime) > gTimeToSync:
                pass#print (" ")
            else:#模擬streaming,等時間到再送
                time.sleep(gTimeToSync-(time.time()-gStartTime))
            gTimeToSync = gTimeToSync + 0.15
            
            #print (" get text from server %s, %f\n" % (res.text, time.time() - gStartTime))
            
            #步驟五:告知語音結束或已有辨識結果時，取得辨識結果
            #當SpeechGot=1或RecognitionDone=1，表示切到語音，有辨識結果，可以停止送語音過來，並取得辨識結果，client需送speechend通知Server停送語音。
            #另一種情形，如果Server還沒切到音，client要主動停止，送SpeechEnd通知Server，告知語音結束，取回辨識結果。
            res_json = json.loads(res.text)
            ResulsStatus = res_json["ResultStatus"]#由回傳的JSON欄位取得辨識狀態與結果
            if(ResulsStatus != "Success"):
                pass
                #print("ErrorMsg:"+res_json["ErrorMessage"])
            else:
                SpeechGot = res_json["SpeechGot"]
                RecognitionDone = res_json["RecognitionDone"]
                if SpeechGot == 1 or RecognitionDone == 1  or (j == lens):
                    #步驟五:告知語音結束或已有辨識結果時，取得辨識結果
                    param = {
                        'Action':'syncData',
                        'AsrReferenceId':handle,
                        'ByteNum':0,
                        'SpeechEnd':'y'
                    }
                    res = session.post(GWurl, headers=header_API_Key, params=param, data="")
                    if str(res.text.encode('utf-8')).find('fail') != -1:
                        pass#print (" No result...")
                    else:
                        pass#print (" final %s, %f\n" % (res.text, time.time() - gStartTime))
                    j = lens+100
                    return res.text

ledw = LOOK.LEDconnect()
au = LOOK.AudioFile("/home/pi/Desktop/mics_hat/siri-sound-effect-hd1.wav")

while __name__ == "__main__":
    ledw.close()
    #Trigger
    flag = True
    while True:
        ledw.wake()
        my_record(flag)
        temp = run()
        output = json.loads(temp)
        print(output['Result'][0])
        if (output['Result'][0]!=''):
            ledw.close()
            break
    au.play()
    au.close()

    while True:
        #STT
        RECORD_SECONDS = 5

        flag = False
        my_record(flag)
        temp = run()
        output = json.loads(temp)
        print(output['Result'][0])
        if output['Result'][0]=='':
            input_text = '再見啾咪'
            print(input_text)
            apiURL = 'https://iot.cht.com.tw/apis/CHTIoT/tts/v1/ch/synthesis'
            my_data = {'inputText':input_text, 'speaker':'tc','outputName':'out.mp3'}
            r = requests.post(apiURL, data = my_data)
            f = json.loads(r.text)['file']

            urlretrieve(f, "out.mp3")
            os.system("aplay out.mp3")
            break

        rt = output['Result'][0]
        inputText = ""
        
        #ledw = LOOK.LEDconnect()
        ledw.speak()

        if rt.find("關燈")>-1:
            faceAPI.face_api('set',0)
            inputText = "好啦已經關了"
        elif rt.find("開燈")>-1:
            faceAPI.face_api('set',1)
            inputText = "才鼻要幫你開呢"
        elif rt.find("拍照")>-1:
            faceAPI.face_api('take')
            inputText = "笑一個"
        elif rt.find("天氣")>-1 or rt.find("溫度")>-1 or rt.find("幾度")>-1:
            ans = faceAPI.face_api('weather','temperature')
            inputText = "今天氣溫是" + ans + "度出門記得防曬以免曬傷喔"
        elif rt.find("空氣")>-1:
            ans = faceAPI.face_api('weather','pm25')
            inputText = "今天的批M二點五是" + ans
        elif rt.find("創建")>-1:
            faceAPI.face_api("create")
            ans = faceAPI.face_api("get")
            inputText = "您的臉群ID是" + ans
        elif rt.find("熱熔槍")>-1 or rt.find("槍")>-1:
            inputText = "就跟你說要在所有的東西都裝上感測器你才能找到他"
        elif rt.find("取消")>-1:
            ledw.close()
            break
        elif rt.find("註冊")>-1:
            ans = faceAPI.face_api('get')
            print(ans)
            inputText = "笑一個"
            faceAPI.face_api('take')
            faceAPI.face_api('add_face', ans)
        else:
            send_data = {"task":rt}
            send_json = json.dumps(send_data)

            r = requests.post("http://140.113.170.46:5000/chat", data=send_json)

            print(r.status_code)
            print(r.text)
            print(json.loads(r.text)['Result'])
            inputText = json.loads(r.text)['Result']#output['Result'][0]

        #TTS
        config = configparser.ConfigParser()
        config.read('cht.conf')
        apiKey = config.get('demo-key', 'apiKey')
        headers = {'X-API-KEY': apiKey}

    
        apiURL = 'https://iot.cht.com.tw/apis/CHTIoT/tts/v1/ch/synthesis'
        my_data = {'inputText': inputText, 'speaker':'tc', 'outputName': 'out.mp3'}

        r = requests.post(apiURL, data = my_data)
        try:
            f = json.loads(r.text)['file']
            urlretrieve(f, "out.mp3")
            os.system("aplay out.mp3")
        except:
            print("No Result")
            

        ledw.close()

