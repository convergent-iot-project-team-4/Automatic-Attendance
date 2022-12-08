import matlab.engine # MATLAB engine API import

def init():
  eng = matlab.engine.start_matlab() # MATLAB engine 객체 생성
  print('1')