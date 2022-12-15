#!usr/bin/python
# -*- coding: utf8 -*-

from typing import List, Dict
from fastapi import FastAPI, WebSocket, Request, File, UploadFile

from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.logger import logger
import time
import asyncio
import matlab.engine # MATLAB engine API import
import os, base64, wave, audioop, json

app = FastAPI()
templates = Jinja2Templates(directory="templates")

professor: Dict[str, WebSocket] = {} # {device_name:WebSocket}
students: Dict[str, WebSocket] = {} # {device_name:WebSocket}
corners:Dict[str, WebSocket] = {} # {device_name:WebSocket}

def BeepBeep(fileA = "devA_25cm.wav", fileB = "devB_25cm.wav") -> float:
    global students, corners, professor
    eng = matlab.engine.start_matlab() # MATLAB engine 객체 생성
    ret = eng.BeepBeep(fileA, fileB, "uploaded_files/chirp.wav")
    print(float(ret))
    return ret

async def send_point(distance: float, websocket: WebSocket, keys_s: str, keys_c: str):
    global students, corners, professor
    # professor 찾기
    await websocket.send_text(json.dumps({
        "type": "noticeToProfessor",
        "corner": keys_c,
        "student": keys_s,
        "distance": distance
    }))

# init
def init(device_name, device_type, websocket):
    global students, corners, professor
    # Professor
    if device_type == "professor":
        professor.update({device_type: websocket})
        return True

    # Student, Corner
    if device_type == "corner":
        corners.update({device_name: websocket})
        return True
    if device_type == "student":
        students.update({device_name: websocket})
        return True
    else:
        return False

def makeFolderAndSaveWavFile(student: Dict[str, WebSocket], corner: Dict[str, WebSocket], body: str, isStudentsRecord: bool):
    global students, corners, professor

    keys_c = list(corner.keys())[0]
    keys_s = list(student.keys())[0]
    
    fileName = textToWAV(body, keys_s, keys_c, isStudentsRecord)
    return fileName

def textToWAV(body:str, keys_s: str, keys_c: str, isStudentsRecord: bool):
    directory = keys_s + "_" + keys_c
    os.makedirs("uploaded_files/" + directory, exist_ok=True)

    if isStudentsRecord:
        fileName = f'uploaded_files/{directory}/{keys_s}_{keys_c}.wav'
    else:
        fileName = f'uploaded_files/{directory}/{keys_c}_{keys_s}.wav'

    # make wav file
    decoded = base64.b64decode(body)
    wav_recover = open(fileName, "wb")
    wav_recover.write(decoded)
    wav_recover.close()

    return fileName

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    global students, corners, professor
    print(f"client connected : {websocket.client}")
    await websocket.accept() # client의 websocket접속 허용
    await websocket.send_text(f"Welcome client : {websocket.client}")

    while True:
        data = await websocket.receive_json()  # client 메시지 수신대기
        print(f"message received : {data} from : {websocket.client}")

        if data["type"] == "init":
            init(data["device_name"], data["device_type"], websocket)
            while True:
                await asyncio.sleep(1.0)
        elif data["type"] == "start":
            if len(students) + len(corners) < 0:
                print("device not enough to start.")
                return False
            else:
                print(students)
                print(corners)
                
                for s_key, student_value in sorted(students.items(),key=lambda x:x[0]):
                    for c_key, corner_value in sorted(corners.items(),key=lambda x:x[0]):
                        await student_value.send_text(f"start_recording")
                        await corner_value.send_text(f"start_recording")
                        await asyncio.sleep(1.0)
                        await student_value.send_text(f"play_chirp")
                        await asyncio.sleep(2.0)
                        data = await student_value.receive_json()
                        print(data)
                        
                        await corner_value.send_text(f"play_chirp")
                        await asyncio.sleep(2.0)
                        data = await corner_value.receive_json()
                        print(data)
                        
                        await student_value.send_text("send_wav_file")
                        await corner_value.send_text("send_wav_file")

                        s_file = await student_value.receive_json()
                        c_file = await corner_value.receive_json()

                        student_file_path = makeFolderAndSaveWavFile({s_key: student_value}, {c_key: corner_value}, s_file["body"], True)
                        corner_file_path = makeFolderAndSaveWavFile({s_key: student_value}, {c_key: corner_value}, c_file["body"], False)

                        distance= BeepBeep(student_file_path, corner_file_path)
                        await send_point(distance, professor["professor"], s_key, c_key)

        else:
            print("정의되지 않은 type입니다.")
    return


# 개발/디버깅용으로 사용할 앱 구동 함수
def run():
    import uvicorn
    uvicorn.run(app, host='172.20.10.3', port='8000')

# python main.py로 실행할경우 수행되는 구문
# uvicorn main:app 으로 실행할 경우 아래 구문은 수행되지 않는다.
if __name__ == "__main__":
    BeepBeep('uploaded_files/X_B/B_X.wav', 'uploaded_files/X_B/X_B.wav')
    # run()