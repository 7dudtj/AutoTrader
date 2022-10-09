# Stock Auto Trader

* 주식 자동매매 프로그램
* <ins>**모든 투자의 책임은 본인에게 있습니다.**</ins>

---

## What is Stock Auto Trader?

Stock Auto Trader는 주식 자동매매 프로그램입니다.  
트레이딩 전략으로 **래리 윌리엄스의 변동성 돌파 전략**을 기반으로 하고있으며,  
추가적인 전략을 통해 기대 수익률을 높이고자 합니다.  

## 추가적인 트레이딩 전략

* 여러개의 종목에 대한 분할매수를 진행하여, 리스크를 낮추고자 합니다.  
* k 값은 0.5로 고정하여, 기대 수익을 높이고자 합니다.  

## 트레이딩 환경

* 대신증권의 CREON Plus API를 이용하여 구현되어 있습니다.  
* Windows OS에서만 트레이딩이 가능합니다. MacOs, Linux 환경에서는 트레이딩이 불가합니다.  
* Slack bot을 이용하여 트레이딩 알림을 받아보는 것을 권장합니다.  

---

## How to use

1. **Auto Trader**를 clone하고, requirements를 설치합니다.  
```
git clone https://github.com/7dudtj/AutoTrader.git
cd AutoTrader
pip install -r requirements.txt
cd StockAutoTrader
```
2. 대신증권 홈페이지를 통해 CREON Plus를 설치합니다.
3. 사용하고자 하는 버전을 선택합니다. 1.3.0 버전을 권장합니다.  
3. keys.txt 파일에서 Key 값을 설정합니다.  
CREON id, CREON pwd, CREON pwdcert, 그리고 Slack bot의 token이 필요합니다.  
주석을 지우고, 해당 라인에 key 값을 입력합니다.  
```
# CREON id
# CREON pwd
# CREON pwdcert
# Slack token
```
4. symbols.txt 파일에 거래하고자 하는 종목들의 종목코드를 입력합니다. 
파일에 예시 종목코드가 기입되어 있습니다.  
```
A250780 A228790 A228800 A305720 A400970 A091170 A102780 A139230 A364970 A139260 A117680 A228810
# 수익률을 위하여, 수수료가 없는 ETF 거래를 권장합니다.
```
5. sat 파일에서 프로그램 종료 옵션을 선택합니다.  (Line 293~306)  
트레이딩 종료 후 컴퓨터 전원을 자동으로 끄고싶을 경우, Line 304의 주석을 해제합니다.  
```
os.system('shutdown -s -t 0')
```
6. sat 파일에서 분할매수하고자 하는 종목의 수를 설정합니다. (Line 323~327)  
기본값은 예수금의 30%씩 3종목에 대한 분할매수입니다.  
```
target_buy_count = 3
buy_percent = 0.3
```
7. 오전 8시 55분에 AutoConnector.py를 실행합니다.  
```
python AutoConnector.py
```
8. 오전 8시 58분에 sat 파일을 실행합니다.
```
python sat_v.1.3.0.py
```
9. 오후 3시 15분~20분에 구매한 종목에 대한 매도가 진행됩니다.  
매도가 끝날 경우 프로그램이 자동 종료됩니다.  

---

## Warning

<p align="center">
  <img width="400" src="https://user-images.githubusercontent.com/67851701/174976264-43524462-13e8-4dda-b66d-2278297aa9a4.jpg">
</p> 

<ins>**모든 투자의 책임은 본인에게 있습니다.**</ins>  
**Stock Auto Trader**는 작은 수익을 가져다줄 수 있지만, 큰 손실을 유발할 수 있습니다.  

주식 투자로 발생하는 모든 손실은 투자자 본인의 책임이며,  
**Stock Auto Trader**의 전략과 코드는 본인의 전략에 맞게 수정한 후 사용하시길를 권장합니다.  
