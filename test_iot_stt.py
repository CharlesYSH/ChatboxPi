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

logging.basicConfig(level=logging.DEBUG, format="%(message)s")

CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 16000
RECORD_SECONDS = 5
WAVE_OUTPUT_FILENAME = "voice.raw"

def my_record():
    p = pyaudio.PyAudio()
    stream = p.open(format = FORMAT,
                channels = CHANNELS,
                rate = RATE,
                input = True,
                frames_per_buffer = CHUNK)
    frames = []
    print("3")
    time.sleep(1)
    print("2")
    time.sleep(1)
    print("1")
    print("START")
    for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
        data = stream.read(CHUNK)
        frames.append(data)
    print("STOP")
        
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


    print('post Action:connect:(',res.text,')')
    print('handle:(',handle,')')

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
                print (" ")
            else:#模擬streaming,等時間到再送
                time.sleep(gTimeToSync-(time.time()-gStartTime))
            gTimeToSync = gTimeToSync + 0.15
            
            print (" get text from server %s, %f\n" % (res.text, time.time() - gStartTime))
            
            #步驟五:告知語音結束或已有辨識結果時，取得辨識結果
            #當SpeechGot=1或RecognitionDone=1，表示切到語音，有辨識結果，可以停止送語音過來，並取得辨識結果，client需送speechend通知Server停送語音。
            #另一種情形，如果Server還沒切到音，client要主動停止，送SpeechEnd通知Server，告知語音結束，取回辨識結果。
            res_json = json.loads(res.text)
            ResulsStatus = res_json["ResultStatus"]#由回傳的JSON欄位取得辨識狀態與結果
            if(ResulsStatus != "Success"):
                print("ErrorMsg:"+res_json["ErrorMessage"])
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
                        print (" No result...")
                    else:
                        print (" final %s, %f\n" % (res.text, time.time() - gStartTime))
                    j = lens+100
                    break

if __name__ == "__main__":
    my_record()
    run()

