# AutoTrader
Auto Trading Program

## CoinAutoTrader
'Coin Auto Trader' by Youngseo Yoo (github.com/7dudtj)  
### Warning!  
This program does not guarantee you to earn money.  
You can lose all of your money by various reasons, including program errors.  
Responsibility of investment is all up to you, and  
responsibility of using this program is all up to you. too.  
This program is made based on Larry Williams' volatility breakthrough strategy.  
I highly recommend you to change this program code by your own trading algorithms and use it.  
This program is made to use 'Upbit' api.  
This program is not developed yet. But if you want to use, then I recommend ver 1.4.

### Ubuntu 서버 명령어

#### <백그라운드 실행>

ver 1.5.1: nohup python3 cat_v.1.5.1.py > output.log &

ver 1.6.3: nohup python3 cat_v.1.6.3.py > output.log &
 
test code: nohup python3 test.py > output.log &

 
#### <실행되고 있는지 확인> 

ps ax | grep .py
 

#### <프로세스 종료>(PID는 ps ax | grep .py를 했을때 확인 가능)

kill -9 PID

#### <서버 업그레이드>

리스트 업데이트: apt-get update 

업그레이드: sudo apt-get upgrade

## License

<img align="right" src="http://opensource.org/trademarks/opensource/OSI-Approved-License-100x137.png">

The class is licensed under the [MIT License](http://opensource.org/licenses/MIT):

Copyright &copy; 2021 [7dudtj](https://github.com/7dudtj).

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
