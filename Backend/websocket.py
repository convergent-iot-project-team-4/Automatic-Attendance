from typing import List
from fastapi import FastAPI, WebSocket, Request, File, UploadFile

from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.logger import logger
import time

app = FastAPI()
# html파일을 서비스할 수 있는 jinja설정 (/templates 폴더사용)
templates = Jinja2Templates(directory="templates")

lock = 0
professor = {}
students = {}
corners = {} # {device_name:IP}

# web sockets; type: [WebSocket]
all_sockets = [] 

def send_point(distance):
    # professor 찾기
    prof_tablet = [x for x in professor if x.client  == websocket_ip][0]
    prof_tablet.send_text(f"A랑 X의 거리는 {distance}야~")

# init
def init(device_name = "", websocket_ip = ""):
    # Professor
    if device_name.lower() == "professor":
        professor[websocket_ip] = device_name
        return True

    # Student, Corner
    if websocket_ip not in [x.client for x in all_sockets]:
        return False
    else:
        t = [x for x in all_sockets if x.client  == websocket_ip]
        all_sockets.remove(t[0])

        if device_name.upper() in ["A", "B", "C", "D"]:
            corners[device_name] = websocket_ip
            return True
        elif device_name.upper() in ["X", "Y", "Z"]:
            students[device_name] = websocket_ip
            return True
        else:
            return False

async def start():
    if len(students) + len(corners) < 4:
        return False
    else:
        # (A => X) chirp 재생
        # A의 websocket 찾기
        await tellDeviceToChirp("A", "X")
        await tellDeviceToChirp("A", "Y")
        await tellDeviceToChirp("A", "Z")
        

async def tellDeviceToChirp(first, second):
    first_send = [x for x in all_sockets if x.client  == students[f"{first}"]][0]
    await first_send.send_text(f"빨리 {second}한테 첩 보내")
    data = await first_send.receive_text()

    second_send = [x for x in all_sockets if x.client  == corners[f"{second}"]][0]
    await second_send.send_text(f"빨리 {first}한테 첩 보내")
    data = await second_send.receive_text()

    first_send.send_text("녹음 그만하고 파일 내 놔")
    await second_send.send_text("녹음 그만하고 파일 내 놔")

    f_file = first_send.receive_bytes()
    s_file = second_send.receive_bytes()

    f = open(f'uploaded_files/{first}_{second}.wav', 'w')
    f.write(f_file)
    f.close()

    f = open(f'uploaded_files/{second}_{first}.wav', 'w')
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
async def receive_audio_files(files: List[bytes] = File(...)):
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
            init(data["device_name"], data["websocket_ip"])
        elif data["type"] == "start":
            start()
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