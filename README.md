# AutoTrader
Coin Auto Trading Program

Ubuntu 서버 명령어

백그라운드 실행:

nohup python3 cat_v.1.0.0.py > output.log &

nohup python3 test.py > output.log &

실행되고 있는지 확인: ps ax | grep .py

프로세스 종료(PID는 ps ax | grep .py를 했을때 확인 가능): kill -9 PID

