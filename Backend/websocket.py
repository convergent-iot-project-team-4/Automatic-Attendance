#!usr/bin/python
# -*- coding: utf8 -*-

from typing import List
from fastapi import FastAPI, WebSocket, Request, File, UploadFile

from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.logger import logger
import time
import asyncio
# import matlab.engine # MATLAB engine API import

app = FastAPI()
templates = Jinja2Templates(directory="templates")

lock = 0
professor = {} # {device_name:WebSocket}
students = {} # {device_name:WebSocket}
corners = {} # {device_name:WebSocket}

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
def init(device_name, websocket):
    # Professor
    if device_name.lower() == "professor":
        professor["professor"] = websocket
        return True

    # Student, Corner
    if device_name.upper() in ["A", "B", "C", "D"]:
        corners[device_name] = websocket
        return True
    elif device_name.upper() in ["X", "Y", "Z"]:
        students[device_name] = websocket
        return True
    else:
        return False

async def start_chirps():
    if len(students) + len(corners) < 0:
        return False
    else:
        # (A => X) chirp 재생
        # A의 websocket 찾기
        await tellDeviceToChirp("X", "A")
        # BeepBeep()

        # await tellDeviceToChirp("A", "Y")
        # await tellDeviceToChirp("A", "Z")
        

async def tellDeviceToChirp(student, corner):
    first_send = students[student]
    second_send = corners[corner]

    await first_send.send_text(f"녹음 시작해")
    await second_send.send_text(f"녹음 시작해")

    await first_send.send_text(f"빨리 {corner}한테 첩 보내")
    print("trying to receive")
    data = await first_send.receive_text()
    print(data)
    # await first_send.receive_text() # 다 했어 받을때까지 기다림 -> 여기서 터짐, 
    # cannot call recv while another coroutine is already waiting for the next message

    await second_send.send_text(f"빨리 {student}한테 첩 보내")
    await second_send.receive_text() # 다 했어 받을때까지 기다림


    first_start_recording = asyncio.create_task(
        first_send.send_text("녹음 그만하고 파일 내 놔")
    )
    second_start_recording = asyncio.create_task(
        second_send.send_text("녹음 그만하고 파일 내 놔")
    )

    await first_start_recording
    await second_start_recording
    

    f_file = await first_send.receive_bytes()
    s_file = await second_send.receive_bytes()

    f = open(f'uploaded_files/{student}_{corner}.wav', 'w')
    f.write(f_file)
    f.close()

    f = open(f'uploaded_files/{corner}_{student}.wav', 'w')
    f.write(s_file)
    f.close()

    return True

async def acquire_lock():
    # lock
    global lock
    if lock == 0:
        lock = 1
        return True
    else:
        return False

def release_lock():
    # lock
    global lock
    if lock == 1:
        lock = 0
        return True
    else:
        return False


@app.get("/client")
async def client(request: Request):
    # /templates/client.html파일을 response함
    return templates.TemplateResponse("client.html", {"request":request})

@app.post("/files/")
async def receive_audio_files(files: List[bytes] = File(...), sender_device_name = "None", receiver_device_name = "None"):
    f = open(f'uploaded_files/{sender_device_name}_{receiver_device_name}.wav', 'w')
    f.write(files)
    f.close()
    return True

@app.get("/test_files/")
async def test_files(files: List[bytes] = File(...)):
    contents = """
        <body>
            <form action="/receive_audio_files/" enctype="multipart/form-data" method="get">
                <input name="files" type="file" multiple>
                <input type="submit">
            </form>
        </body>
    """
    return HTMLResponse(content=contents)
  
# 웹소켓 설정 ws://127.0.0.1:8000/ws 로 접속할 수 있음
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    print(f"client connected : {websocket.client}")
    await websocket.accept() # client의 websocket접속 허용
    await websocket.send_text(f"Welcome client : {websocket.client}")
    all_sockets.append(websocket)

    while True:
        data = await websocket.receive_json()  # client 메시지 수신대기
        print(f"message received : {data} from : {websocket.client}")

        if data["type"] == "init":
            init(data["device_name"], websocket)
        elif data["type"] == "start":
            await start_chirps()
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