import matlab.engine         # MATLAB engine API import
eng = matlab.engine.start_matlab()  # MATLAB engine 객체 생성
ret = eng.triarea(1.0,5.0)
print(ret)