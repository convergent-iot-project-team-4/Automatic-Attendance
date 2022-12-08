import matlab.engine # MATLAB engine API import

def init():
  eng = matlab.engine.start_matlab() # MATLAB engine 객체 생성
  ret = eng.BeepBeep("devA_25cm.wav", "devB_25cm.wav", "chirp.wav")
  print(ret)

init()