#!usr/bin/python
# -*- coding: utf8 -*-

from typing import List
from fastapi import FastAPI, WebSocket, Request, File, UploadFile

from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.logger import logger
import time
import asyncio
import matlab.engine # MATLAB engine API import

app = FastAPI()
templates = Jinja2Templates(directory="templates")

professor: dict[str, WebSocket] = {} # {device_name:WebSocket}
students: dict[str, WebSocket] = {} # {device_name:WebSocket}
corners: dict[str, WebSocket] = {} # {device_name:WebSocket}

# web sockets; type: [WebSocket]
all_sockets: list[WebSocket] = []

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
def init(device_name:str, device_type: str, websocket):
    global professor
    global corners
    global students

    # Professor
    if device_type == "professor":
        professor["professor"] = websocket
        return True

    # Student, Corner
    if device_type == "corner":
        corners[device_name] = websocket
        return True
    if device_type == "student":
        students[device_name] = websocket
        return True
    else:
        return False

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    global students, corners, professor

    print(f"client connected : {websocket.client}")
    await websocket.accept() # client의 websocket접속 허용
    await websocket.send_text(f"Welcome client : {websocket.client}")
    all_sockets.append(websocket)

    while True:
        data = await websocket.receive_json()  # client 메시지 수신대기
        print(f"message received : {data} from : {websocket.client}")

        if data["type"] == "init":
            init(data["device_name"], websocket)
            # sort students, corners via name
            students = sorted(students, key=lambda x:x[0])
            corners = sorted(corners, key=lambda x:x[0])

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

                        f_file = await first_send.receive_bytes()
                        s_file = await second_send.receive_bytes()

                        f = open(f'uploaded_files/{student}_{corner}.wav', 'w')
                        f.write(f_file)
                        f.close()

                        f = open(f'uploaded_files/{corner}_{student}.wav', 'w')
                        f.write(s_file)
                        f.close()
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