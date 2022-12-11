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
import os, base64

app = FastAPI()
templates = Jinja2Templates(directory="templates")

professor: Dict[str, WebSocket] = {} # {device_name:WebSocket}
students: Dict[str, WebSocket] = {} # {device_name:WebSocket}
corners:Dict[str, WebSocket] = {} # {device_name:WebSocket}

# web sockets; type: [WebSocket]
all_sockets = []

def BeepBeep(fileA = "devA_25cm.wav", fileB = "devB_25cm.wav", chirp="chirp.wav"):
    eng = matlab.engine.start_matlab() # MATLAB engine 객체 생성
    ret = eng.BeepBeep(fileA, fileB, chirp)
    print(ret)
    return ret

def send_point(distance, websocket):
    # professor 찾기
    prof_tablet = websocket
    prof_tablet.send_text(distance)

# init
def init(device_name, device_type, websocket):
    global professor
    global corners
    global students

    # Professor
    if device_type == "professor":
        corners.update({device_name: websocket})
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

def makeFolderAndSaveWavFile(student, corner, body, isStudentsRecord):
    directory = student+ "_" + corner
    os.makedirs("uploaded_files/" + directory, exist_ok=True)

    if isStudentsRecord:
        fileName = 'uploaded_files/{directory}/{student}_{corner}.wav'
    else:
        fileName = 'uploaded_files/{directory}/{corner}_{student}.wav'
    
    wav_file = open(fileName, "wb")
    decode_string = base64.b64decode(body)
    wav_file.write(decode_string)

    return

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
            # sort students, corners via name
            students = sorted(students.items())
            corners = sorted(corners.items())
            while True:
                await asyncio.sleep(1.0)
        elif data["type"] == "start":
            if len(students) + len(corners) < 0:
                return False
            else:
                for student in students:
                    for corner in corners:
                        await student.send_text(f"start_recording")
                        await corner.send_text(f"start_recording")

                        
                        await student.send_text(f"play_chirp")
                        data = await student.receive_json()
                        print(data)
                        
                        await corner.send_text(f"play_chirp")
                        data = await corner.receive_json()
                        print(data)
                        
                        await student.send_text("send_wav_file")
                        await corner.send_text("send_wav_file")

                        s_file = await student.receive_json()
                        c_file = await corner.receive_json()

                        makeFolderAndSaveWavFile(student, corner, s_file["body"], True)
                        makeFolderAndSaveWavFile(student, corner, c_file["body"], False)

        else:
            print("정의되지 않은 type입니다.")
    return


# 개발/디버깅용으로 사용할 앱 구동 함수
def run():
    import uvicorn
    uvicorn.run(app, host='0.0.0.0', port='8000')

# python main.py로 실행할경우 수행되는 구문
# uvicorn main:app 으로 실행할 경우 아래 구문은 수행되지 않는다.
if __name__ == "__main__":
    run()