"""
    'Coin Auto Trader' by Youngseo Yoo (github.com/7dudtj)
    Warning!
    This program does not guarantee you to earn money.
    You can lose all of your money by various reasons, including program errors.
    Responsibility of investment is all up to you, and
    responsibility of using this program is all up to you. too.
    This program is made based on Larry Williams' volatility breakthrough strategy.
    I highly recommend you to change this program code by your own trading algorithms and use it.
    This program is made to use 'Bithumb' api.
    You might need to install some modules for using this program.
"""

import sys
from PyQt5 import uic
from PyQt5.QtWidgets import QApplication, QMainWindow
from pybithumb import Bithumb
import pybithumb
import datetime
from PyQt5.QtCore import QThread, pyqtSignal
from volatility import *
import requests

class VolatilityWorker(QThread):
    tradingSent = pyqtSignal(str, str, str)

    def __init__(self, ticker, bithumb):
        super().__init__()
        self.ticker = ticker
        self.bithumb = bithumb
        self.alive = True
        self.myToken = "slack token"

    def run(self):
        now = datetime.datetime.now()
        mid = datetime.datetime(now.year, now.month, now.day) + datetime.timedelta(1)
        ma5 = get_yesterday_ma5(self.ticker)
        target_price = get_target_price(self.ticker)
        wait_flag = False
        print("target price :", target_price)
        self.post_message(self.myToken, "#coin", self.ticker + " 매수 목표가: ￦"+str(target_price))
        while self.alive:
            try:
                now = datetime.datetime.now()
                if mid < now < mid + datetime.delta(seconds=60):
                    target_price = get_target_price(self.ticker)
                    mid = datetime.datetime(now.year, now.month, now.day) + datetime.timedelta(1)
                    ma5 = get_yesterday_ma5(self.ticker)
                    desc = sell_crypto_currency(self.bithumb, self.ticker)

                    result = self.bithumb.get_order_completed(desc)
                    timestamp = result['data']['order_date']
                    dt = datetime.datetime.fromtimestamp( int(int(timestamp)/1000000) )
                    tstring = dt.strftime("%Y/%m/%d %H:%M:%S")
                    self.tradingSent.emit(tstring, "매도", result['data']['order_qty'])
                    self.post_message(self.myToken, "#coin", tstring+" "+result['data']['order_qty']+
                                      " "+self.ticker+" 매도")
                    tstring = dt.strftime("%Y/%m/%d")
                    self.post_message(self.myToken, "#coin", tstring+" 오늘의 매수 목표가: "+target_price)
                    wait_flag = False

                if wait_flag == False:
                    current_price = pybithumb.get_current_price(self.ticker)
                    if (current_price >= target_price) and (current_price >= ma5):
                        desc = buy_crypto_currency(self.bithumb, self.ticker)
                        result = self.bithumb.get_order_completed(desc)
                        timestamp = result['data']['order_date']
                        dt = datetime.datetime.fromtimestamp( int(int(timestamp)/1000000) )
                        tstring = dt.strftime("%Y/%m/%d %H:%M:%S")
                        self.tradingSent.emit(tstring, "매수", result['data']['order_qty'])
                        self.post_message(self.myToken, "#coin", tstring + " " + result['data']['order_qty'] +
                                          " " + self.ticker + " 매수")
                        wait_flag = True
            except:
                pass
            time.sleep(1)

    def close(self):
        self.alive = False

    def post_message(self, token, channel, text):
        response = requests.post("https://slack.com/api/chat.postMessage",
                                 headers={"Authorization": "Bearer "+token},
                                 data={"channel": channel, "text": text}
                                 )
        print(response)

form_class = uic.loadUiType("resource/main.ui")[0]

class MainWindow(QMainWindow, form_class):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.ticker = "" # set target ticker
        self.button.clicked.connect(self.clickBtn)
        self.setWindowTitle("Home Trading System")
        self.myToken = "slack token"

        with open("bithumb.txt") as f:
            lines = f.readlines()
            apikey = lines[0].strip()
            seckey = lines[1].strip()
            self.apiKey.setText(apikey)
            self.secKey.setText(seckey)

    def clickBtn(self):
        if self.button.text() == "매매시작":
            apiKey = self.apiKey.text()
            secKey = self.secKey.text()
            if len(apiKey) != 32 or len(secKey) != 32:
                self.textEdit.append("KEY가 올바르지 않습니다.")
                return
            else:
                self.bithumb = Bithumb(apiKey, secKey)
                self.balance = self.bithumb.get_balance(self.ticker)
                if self.balance == None:
                    self.textEdit.append("KEY가 올바르지 않습니다.")
                    return

            self.button.setText("매매중지")
            self.textEdit.append("------ START ------")
            self.textEdit.append(f"보유 현금 : {self.balance[2]} 원")

            self.vw = VolatilityWorker(self.ticker, self.bithumb)
            self.vw.tradingSent.connect(self.receiveTradingSignal)
            self.vw.start()
            self.post_message(self.myToken, "#coin", "CAT 매매시작 (bithumb)")
        else:
            self.vw.close()
            self.textEdit.append("------- END -------")
            self.button.setText("매매시작")
            self.post_message(self.myToken, "#coin", "CAT 매매종료 (bithumb)")

    def receiveTradingSignal(self, time, type, amount):
        self.textEdit.append(f"[{time}] {type} : {amount}")

    def closeEvent(self, event):
        self.vw.close()
        self.widget.closeEvent(event)
        self.widget_2.closeEvent(event)
        self.widget_3.closeEvent(event)

    def post_message(self, token, channel, text):
        response = requests.post("https://slack.com/api/chat.postMessage",
                                 headers={"Authorization": "Bearer "+token},
                                 data={"channel": channel, "text": text}
                                 )
        print(response)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    mw = MainWindow()
    mw.show()
    exit(app.exec_())