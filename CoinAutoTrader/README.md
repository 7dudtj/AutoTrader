# Coin Auto Trader

* 암호화폐 자동매매 프로그램
* <ins>**모든 투자의 책임은 본인에게 있습니다.**</ins>

---

## What is Coin Auto Trader?

Coin Auto Trader는 암호화폐 자동매매 프로그램입니다.  
트레이딩 전략으로 **래리 윌리엄스의 변동성 돌파 전략**을 기반으로 하고있으며,  
추가적인 전략을 통해 기대 수익률을 높이고자 합니다.  

## 추가적인 트레이딩 전략

* 구매한 코인의 가격이 시초가의 98% 미만으로 떨어질 경우, 큰 손실 방지를 위해 코인을 매도합니다.   
* 코인 구매 후 30분 이내에 5% 이상의 수익이 발생할 경우, 매도를 진행하여 수익을 얻습니다.  
* 코인 구매 후 30분 이상 2시간 이내에 1%의 수익이 발생할 경우, 매도를 진행하여 수익을 얻습니다.  
* 그 외의 경우, 현재 가격이 구매 가격 이상일 경우, 매도를 진행하여 원금을 보전합니다.  
* 매도되지 않은 코인은 다음날 오전 8시 59분에 전부 매도되며, 손실이 발생할 수 있습니다.  

## 트레이딩 환경

* Upbit API를 이용하여 구현되어 있습니다.  
* AWS 환경에서 운용하는 것을 권장합니다.  
* Slack bot을 이용하여 트레이딩 알림을 받아보는 것을 권장합니다.  

---

## How to use

1. **Auto Trader**를 clone하고, requirements를 설치합니다.  
```
git clone https://github.com/7dudtj/AutoTrader.git
cd AutoTrader
pip install -r requirements.txt
cd CoinAutoTrader
```
2. 사용하고자 하는 버전을 선택합니다. 1.6.4 버전을 권장합니다.  
3. cat 파일에서 Key 값을 설정합니다.  (Line 22~24)  
Upbit access key, Upbit secret key, 그리고 Slack bot의 token이 필요합니다.  
```
# set keys
access = "" # fill upbit access key
secret = "" # fill upbit secret key
myToken = "" # fill slack bot's token
```
4. cat 파일에서 트레이딩 하고자 하는 암호화폐의 tickers를 입력합니다.
```
tickers = {} # fill tickers information by guide line
# see cat file's line 104~107
```
5. cat 파일에서 k 값을 설정합니다. k 값은 0.5~0.7을 권장합니다.
```
k = 0.5 # choose k value that you want (at line 114)
```
6. cat 파일을 실행합니다. 프로그램은 종료 전까지 항상 작동합니다.  
```
python cat_v.1.6.4.py
```

---

## Warning

<p align="center">
  <img width="400" src="https://user-images.githubusercontent.com/67851701/174976264-43524462-13e8-4dda-b66d-2278297aa9a4.jpg">
</p> 

<ins>**모든 투자의 책임은 본인에게 있습니다.**</ins>  
**Coin Auto Trader**는 작은 수익을 가져다줄 수 있지만, 큰 손실을 유발할 수 있습니다.  

암호화폐 투자로 발생하는 모든 손실은 투자자 본인의 책임이며,  
**Coin Auto Trader**의 전략과 코드는 본인의 전략에 맞게 수정한 후 사용하시길를 권장합니다.  
