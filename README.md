# Automatic Attendance system for Convergent IoT Team Project

## server: Python with MATLAB library
* install
  * `cd "matlabroot/extern/engines/python"`
  * `python setup.py install`
  * For more info, ref [here](https://sweetdev.tistory.com/1209)

## 실시간성
  * web socket

## client for student: Android App
* Mimium Android Version: 
* Soundpool쓰면됨

낮을수록 좋다

데모니까 라이브서비스는 아니여도 되지만
Continuous하진 않아도 된다.

마이크가 마주보게

## client for instructor: WEB?

## REST APIs
* [POST]/update
* body 
{
  "sender": "A",
  "timestamp": ""~""
  "file": ~~
}
// TODO: file with post

## WebSoket API
* get_update
* `pip install websocket`
* `pip install uvicorn`
* `pip install wsproto`