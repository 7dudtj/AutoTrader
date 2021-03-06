"""
    'Coin Auto Trader' by Youngseo Yoo (github.com/7dudtj)
    Warning!
    This program does not guarantee you to earn money.
    You can lose all of your money by various reasons, including program errors.
    Responsibility of investment is all up to you, and
    responsibility of using this program is all up to you. too.
    This program is made based on Larry Williams' volatility breakthrough strategy.
    I highly recommend you to change this program code by your own trading algorithms and use it.
    This program is made to use 'Upbit' api.
"""


# import modules
import time
import pyupbit
import datetime
import requests


# set keys
access = "" # upbit access key
secret = "" # upbit secret key
myToken = "" # slack token


# functions ------------------------------------------------------------------------------
# set ticker (target price, attain target price, danger) >> 10/s
def set_ticker(ticker, k):
    # get target price
    df = pyupbit.get_ohlcv(ticker, interval="day", count=6)
    target_price = df.iloc[-2]['close'] + (df.iloc[-2]['high'] - df.iloc[-2]['low']) * k
    ma5 = df['close'].rolling(5).mean().iloc[-2]
    target = 0
    danger = False
    if target_price >= ma5:
        target = target_price
    else:
        target = ma5
        danger = True # target_price < ma5: danger 

    # find dangerous situation (1)
    range = 0.08
    if df.iloc[-2]['low'] * range <= (df.iloc[-2]['high'] - df.iloc[-2]['low']):
        danger = True

    # find dangerous situation (2)
    if (df.iloc[-2]['close'] < ma5):
        danger = True

    # return [target, attain(False), danger]
    return target, False, danger

# set tickers >> 0.1s * (number of tickers)
def set_tickers(tickers, new_start):
    try:
        for ticker in tickers:
            tickers[ticker][0], tickers[ticker][1], tickers[ticker][2] = set_ticker(ticker, k)
            if (new_start):
                df = pyupbit.get_ohlcv(ticker, interval="day", count=2)
                if tickers[ticker][0] <= df.iloc[1]['high']:
                    tickers[ticker][1] = True
                time.sleep(0.1)
            time.sleep(0.1)
        if (new_start): 
            post_message(myToken, "#coin", "Get tickers information successfully!")
    except Exception as e:
        post_message(myToken, "#coin", "Error: "+str(e)+"\nReset tickers")
        set_tickers(tickers, new_start)

# 09:00 >> 10/s
def get_start_time():
    df = pyupbit.get_ohlcv("KRW-BTC", interval="day", count=1)
    start_time = df.index[0]
    return start_time

# get my coin balance >> 30/s
def get_balance(ticker):
    balances = upbit.get_balances()
    for b in balances:
        if b['currency'] == ticker:
            if b['balance'] is not None:
                return float(b['balance'])
            else:
                return 0
    return 0

# get 1st ask price >> 10/s
def get_current_price(ticker):
    return pyupbit.get_orderbook(tickers=ticker)[0]["orderbook_units"][0]["ask_price"]

# send slack message
def post_message(token, channel, text):
    response = requests.post("https://slack.com/api/chat.postMessage",
                             headers={"Authorization": "Bearer " + token},
                             data={"channel": channel, "text": text}
                             )
    print(response)

# buy & sell >> 8/s
# ----------------------------------------------------------------------------------------


# tickers = {ticker: [target, attain, danger]}
# choose tickers you want to trade
# ex) tickers = {'KRW-BTC': [0, False, False]}
tickers = {}


# set needed variables and start program
now = datetime.datetime.now() + datetime.timedelta(hours=9) # change hours by your server time
buy_time = now
upbit = pyupbit.Upbit(access, secret)
k = 0.5 # low k: high risk, high return
current_ticker = ""
current_open = 0
change_state = False
buy = False
today_buy = True
tomorrow_buy = True
today_start = False
start_time = get_start_time()
end_time = start_time + datetime.timedelta(days=1)
money = get_balance("KRW")
buy_price = 0
sell_price = 0
today_buy_count = 0
time.sleep(0.2)
post_message(myToken, "#coin", "Start CAT_1.6.4!\n"+str(now.replace(microsecond=0)))
post_message(myToken, "#coin", "Account balance: "+str(int(money))+"won")

# set tickers information for the first time
set_tickers(tickers, True)

# main process
while True:
    try:
        # get current time
        now = datetime.datetime.now() + datetime.timedelta(hours=9)
        # 09:00:00 ~ 08:59:00: main loop
        if start_time < now <= end_time - datetime.timedelta(minutes=1):
            # start new day
            if today_start is True:
                post_message(myToken, "#coin", "----------------------------------------\n"
                                               "----------------------------------------\n"
                                               "Good morning! CAT start!\n"+str(now.replace(microsecond=0)))
                post_message(myToken, "#coin", "Today's trading? "+str(today_buy))
                krw = get_balance("KRW")
                post_message(myToken, "#coin", "Account balance: " + str(int(krw)) + "won")
                today_start = False
                change_state = False
            # search tickers
            for ticker in tickers:
                # get current price steadily
                current_price = get_current_price(ticker)
                # reaching target price for the first time
                if tickers[ticker][0] <= current_price and tickers[ticker][1] is False:
                    # check: attain
                    tickers[ticker][1] = True
                    # buy: false & not dangerous & 09:30 ~ 07:00 & buy_count < 1 >> do buy
                    if buy is False and today_buy is True and tickers[ticker][2] is False and today_buy_count < 1\
                            and (start_time + datetime.timedelta(minutes=30) <= now < start_time + datetime.timedelta(hours=22)):
                        krw = get_balance("KRW")
                        buy_price = current_price
                        upbit.buy_market_order(ticker, krw*0.9995) # buy: market order
                        buy = True
                        tickers[ticker][2] = True
                        today_buy_count += 1
                        now = datetime.datetime.now() + datetime.timedelta(hours=9)
                        buy_time = now
                        current_ticker = ticker
                        df = pyupbit.get_ohlcv(current_ticker, interval="day", count=1)
                        current_open = df.iloc[0]['open']
                        post_message(myToken, "#coin", "-----------------------------------------\\\n"
                                                       "Buy "+current_ticker+": "+str(int(krw*0.9995))+"won\n"+str(now.replace(microsecond=0)))
                        post_message(myToken, "#coin", "Buy price: "+str(buy_price))
                        time.sleep(0.3)
                # my coin rises 5% already: sell coin
                # or
                # current price goes below -2% of open price: emergency sell
                if buy is True and ticker == current_ticker and \
                        (current_price >= buy_price * 1.05 or current_price < current_open * 0.98):
                    sell_price = current_price
                    coin = get_balance(current_ticker[4:])
                    upbit.sell_market_order(current_ticker, coin) # sell: market order
                    buy = False
                    now = datetime.datetime.now() + datetime.timedelta(hours=9)
                    if current_price < current_open * 0.98:
                        post_message(myToken, "#coin", "Safety net operation. Emergency sell!\nStop trading until tomorrow.")
                        today_buy = False
                        tomorrow_buy = False
                    else:
                        post_message(myToken, "#coin", "Get 5%!")
                    post_message(myToken, "#coin", "Sell "+str(coin)+" "+current_ticker+"\n"+str(now.replace(microsecond=0)))
                    post_message(myToken, "#coin", "Sell price: "+str(sell_price))
                    krw = get_balance("KRW")
                    post_message(myToken, "#coin", "Account balance: "+str(int(krw))+"won\n"
                                                    "-----------------------------------------/")
                    # reset data
                    current_ticker = ""
                    current_open = 0
                    buy_price = 0
                    sell_price = 0
                    time.sleep(0.2)
                # do not rise 5% in 30 minutes: try to sell at 1% margin
                if buy is True and ticker == current_ticker and \
                        now > buy_time + datetime.timedelta(minutes=30) and current_price >= buy_price * 1.01:
                    sell_price = current_price
                    coin = get_balance(current_ticker[4:])
                    upbit.sell_market_order(current_ticker, coin)  # sell: market order
                    buy = False
                    now = datetime.datetime.now() + datetime.timedelta(hours=9)
                    post_message(myToken, "#coin", "Get 1%!")
                    post_message(myToken, "#coin", "Sell " + str(coin) + " " + current_ticker + "\n" + str(now.replace(microsecond=0)))
                    post_message(myToken, "#coin", "Sell price: " + str(sell_price))
                    krw = get_balance("KRW")
                    post_message(myToken, "#coin", "Account balance: " + str(int(krw)) + "won\n"
                                                    "-----------------------------------------/")
                    # reset data
                    current_ticker = ""
                    current_open = 0
                    buy_price = 0
                    sell_price = 0
                    time.sleep(0.2)
                # do not rise 1% in 2 hours: try to sell at prime cost
                if buy is True and ticker == current_ticker and \
                    now > buy_time + datetime.timedelta(hours=2) and current_price >= buy_price:
                    sell_price = current_price
                    coin = get_balance(current_ticker[4:])
                    upbit.sell_market_order(current_ticker, coin)  # sell: market order
                    buy = False
                    today_buy = False
                    now = datetime.datetime.now() + datetime.timedelta(hours=9)
                    post_message(myToken, "#coin", "Get 0%!\nStop today's trading.")
                    post_message(myToken, "#coin",
                                 "Sell " + str(coin) + " " + current_ticker + "\n" + str(now.replace(microsecond=0)))
                    post_message(myToken, "#coin", "Sell price: " + str(sell_price))
                    krw = get_balance("KRW")
                    post_message(myToken, "#coin", "Account balance: " + str(int(krw)) + "won\n"
                                                    "-----------------------------------------/")
                    # reset data
                    current_ticker = ""
                    current_open = 0
                    buy_price = 0
                    sell_price = 0
                    time.sleep(0.2)
                # get time for tickers iteration
                time.sleep(0.1)

        # 08:59:00 ~ 09:00:00 / sell time (60s)
        else:
            if buy is True:
                sell_price = get_current_price(current_ticker)
                coin = get_balance(current_ticker[4:])
                upbit.sell_market_order(current_ticker, coin) # sell: market order
                buy = False
                now = datetime.datetime.now() + datetime.timedelta(hours=9)
                post_message(myToken, "#coin", "Sell "+str(coin)+" "+current_ticker+"\n"+str(now.replace(microsecond=0)))
                post_message(myToken, "#coin", "Sell price: "+str(sell_price))
                krw = get_balance("KRW")
                post_message(myToken, "#coin", "Account balance: " + str(int(krw)) + "won\n"
                                                "-----------------------------------------/")
                # reset data
                current_ticker = ""
                current_open = 0
                buy_price = 0
                sell_price = 0
                time.sleep(0.3)
            # change buy status
            if change_state is False:
                if today_buy is False and tomorrow_buy is True:
                    today_buy = True   
                elif today_buy is False and tomorrow_buy is False:
                    tomorrow_buy = True
                change_state = True
            # after 09:00:00 >> time change
            start_time = get_start_time()
            today_start = True
            today_buy_count = 0
            time.sleep(0.1)
            end_time = start_time + datetime.timedelta(days=1)
            set_tickers(tickers, False)
    except Exception as e:
        post_message(myToken, "#coin", "Error: "+str(e))
        time.sleep(1)
