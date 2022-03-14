"""
    'Stock Auto Trader' by Youngseo Yoo (github.com/7dudtj)
    Warning!
    This program does not guarantee you to earn money.
    You can lose all of your money by various reasons, including program errors.
    Responsibility of investment is all up to you, and
    responsibility of using this program is all up to you. too.
    This program is made based on Larry Williams' volatility breakthrough strategy.
    I highly recommend you to change this program code by your own trading algorithms and use it.
    This program is made to use 'Creon' api.

    'sat_v.1.2.2.py' will automatically trade Stocks at Korea Stock Market.

    This program only runs on Windows by 32bit python.
    Your computer's OS must be Windows, and you have to run this program at 32bit python.

    Warning! This program is not developed yet.
"""

# import libraries
import sys, ctypes, time, requests, os
import win32com.client
import pandas as pd
from datetime import datetime


# get slack token
with open('keys.txt') as f:
    lines = f.readlines()
    token = lines[3].strip()


# CREON PLUS common objects
cpCodeMgr = win32com.client.Dispatch('CpUtil.CpStockCode')
cpStatus = win32com.client.Dispatch('CpUtil.CpCybos')
cpTradeUtil = win32com.client.Dispatch('CpTrade.CpTdUtil')
cpStock = win32com.client.Dispatch('DsCbo1.StockMst')
cpOhlc = win32com.client.Dispatch('CpSysDib.StockChart')
cpBalance = win32com.client.Dispatch('CpTrade.CpTd6033')
cpCash = win32com.client.Dispatch('CpTrade.CpTdNew5331A')
cpOrder = win32com.client.Dispatch('CpTrade.CpTd0311')


# functions ----------------------------------------------------------------------
# send slack message
def post_message(token, channel, text):
    response = requests.post("https://slack.com/api/chat.postMessage",
        headers={"Authorization": "Bearer " + token},
        data={"channel": channel, "text": text})
    print(response)


# print log
def printlog(message, *args):
    print(datetime.now().strftime('[%m/%d %H:%M:%S]'), message, *args)


# check creon system
def check_creon_system():
    # Whether the process is executed with administrator authority.
    if not ctypes.windll.shell32.IsUserAnAdmin():
        printlog('check_creon_system() : admin user -> FAILED')
        return False

    # Check if it's connected.
    if (cpStatus.IsConnect == 0):
        printlog('check_creon_system() : connect to server -> FAILED')
        return False

    # Order-related initialization
    # - Use only when there's an account-related code. -
    if (cpTradeUtil.TradeInit(0) != 0):
        printlog('check_creon_system() : init trade -> FAILED')
        return False
    return True


# get current price
def get_current_price(code):
    cpStock.SetInputValue(0, code)  # Price information for the item code.
    cpStock.BlockRequest()
    item = {}
    item['cur_price'] = cpStock.GetHeaderValue(11)  # current price
    item['ask'] = cpStock.GetHeaderValue(16)  # bid price
    item['bid'] = cpStock.GetHeaderValue(17)  # ask price
    return item['cur_price'], item['ask'], item['bid']


# get ohlc
def get_ohlc(code, qty):
    cpOhlc.SetInputValue(0, code)  # item code
    cpOhlc.SetInputValue(1, ord('2'))  # 1:period, 2:number
    cpOhlc.SetInputValue(4, qty)  # request number
    cpOhlc.SetInputValue(5, [0, 2, 3, 4, 5])  # 0:date, 2~5:OHLC
    cpOhlc.SetInputValue(6, ord('D'))  # D:day
    cpOhlc.SetInputValue(9, ord('1'))  # 0:Un-modified price, 1:Modified price
    cpOhlc.BlockRequest()
    count = cpOhlc.GetHeaderValue(3)  # 3:recieved number
    columns = ['open', 'high', 'low', 'close']
    index = []
    rows = []
    for i in range(count):
        index.append(cpOhlc.GetDataValue(0, i))
        rows.append([cpOhlc.GetDataValue(1, i), cpOhlc.GetDataValue(2, i),
                     cpOhlc.GetDataValue(3, i), cpOhlc.GetDataValue(4, i)])
    df = pd.DataFrame(rows, columns=columns, index=index)
    return df


# get stock balance ('ALL' or 'stock_code')
def get_stock_balance(code):
    cpTradeUtil.TradeInit()
    acc = cpTradeUtil.AccountNumber[0]  # account number
    accFlag = cpTradeUtil.GoodsList(acc, 1)  # -1:total, 1:stock, 2:futures/option
    cpBalance.SetInputValue(0, acc)  # account number
    cpBalance.SetInputValue(1, accFlag[0])
    cpBalance.SetInputValue(2, 50)
    cpBalance.BlockRequest()
    if code == 'ALL':
        post_message(token, '#stock', datetime.now().strftime('[%m/%d %H:%M:%S]')+'\n'
                     'Account Name: ' + str(cpBalance.GetHeaderValue(0))+'\n'
                     'Evaluation amount: ' + str(cpBalance.GetHeaderValue(3))+'won\n'
                     'Evaluation profit and loss: ' + str(cpBalance.GetHeaderValue(4))+'won\n'
                     'Number of items: ' + str(cpBalance.GetHeaderValue(7)))
    stocks = []
    for i in range(cpBalance.GetHeaderValue(7)):
        stock_code = cpBalance.GetDataValue(12, i)  # item code
        stock_name = cpBalance.GetDataValue(0, i)  # item name
        stock_qty = cpBalance.GetDataValue(15, i)  # count
        if code == 'ALL':
            post_message(token, '#stock', str(i + 1) + ' - ' + stock_code + '(' + stock_name + ')'
                   + ' : ' + str(stock_qty))
            stocks.append({'code': stock_code, 'name': stock_name,
                           'qty': stock_qty})
        if stock_code == code:
            return stock_name, stock_qty
    if code == 'ALL':
        return stocks
    else:
        stock_name = cpCodeMgr.CodeToName(code)
        return stock_name, 0


# get current cash
def get_current_cash():
    cpTradeUtil.TradeInit()
    acc = cpTradeUtil.AccountNumber[0]  # account name
    accFlag = cpTradeUtil.GoodsList(acc, 1)  # -1:total, 1:stock, 2:futures/option
    cpCash.SetInputValue(0, acc)  # account number
    cpCash.SetInputValue(1, accFlag[0])
    cpCash.BlockRequest()
    return cpCash.GetHeaderValue(9)


# get target price
def get_target_price(code):
    try:
        time_now = datetime.now()
        str_today = time_now.strftime('%Y%m%d')
        ohlc = get_ohlc(code, 10)
        if str_today == str(ohlc.iloc[0].name):
            today_open = ohlc.iloc[0].open
            lastday = ohlc.iloc[1]
        else:
            lastday = ohlc.iloc[0]
            today_open = lastday[3]
        lastday_high = lastday[1]
        lastday_low = lastday[2]
        target_price = today_open + (lastday_high - lastday_low) * 0.5
        return target_price
    except Exception as ex:
        post_message(token, '#stock', datetime.now().strftime('[%m/%d %H:%M:%S]')+'\n'
                                "`get_target_price() -> exception! " + str(ex) + "`")
        return None


# get moving average(ex) 5, 10, 20...)
def get_movingaverage(code, window):
    try:
        time_now = datetime.now()
        str_today = time_now.strftime('%Y%m%d')
        ohlc = get_ohlc(code, 20)
        if str_today == str(ohlc.iloc[0].name):
            lastday = ohlc.iloc[1].name
        else:
            lastday = ohlc.iloc[0].name
        closes = ohlc['close'].sort_index()
        ma = closes.rolling(window=window).mean()
        return ma.loc[lastday]
    except Exception as ex:
        post_message(token, '#stock', datetime.now().strftime('[%m/%d %H:%M:%S]')+'\n'
                    'get_movingaverage(' + str(window) + ') -> exception! ' + str(ex))
        return None


# buy etf
def buy_etf(code):
    try:
        global bought_list
        if code in bought_list:
            return False
        time_now = datetime.now()
        current_price, ask_price, bid_price = get_current_price(code)
        target_price = get_target_price(code)  # target price
        ma5_price = get_movingaverage(code, 5)  # ma5
        ma10_price = get_movingaverage(code, 10)  # ma10
        buy_qty = 0
        if ask_price > 0:
            buy_qty = buy_amount // ask_price
        stock_name, stock_qty = get_stock_balance(code)
        if current_price > target_price and current_price > ma5_price \
                and current_price > ma10_price:
            printlog(stock_name + '(' + str(code) + ') ' + str(buy_qty) +
                     'EA : ' + str(current_price) + ' meets the buy condition!`')
            cpTradeUtil.TradeInit()
            acc = cpTradeUtil.AccountNumber[0]  # account number
            accFlag = cpTradeUtil.GoodsList(acc, 1)  # -1:total,1:stock,2:futures/option
            cpOrder.SetInputValue(0, "2")  # 2: ask
            cpOrder.SetInputValue(1, acc)  # account number
            cpOrder.SetInputValue(2, accFlag[0])
            cpOrder.SetInputValue(3, code)  # item code
            cpOrder.SetInputValue(4, buy_qty)
            cpOrder.SetInputValue(7, "2")  # option >> 0:basic, 1:IOC, 2:FOK
            cpOrder.SetInputValue(8, "12")
            ret = cpOrder.BlockRequest()
            rqStatus = cpOrder.GetDibStatus()
            errMsg = cpOrder.GetDibMsg1()
            printlog('FoK buy ->', stock_name, code, buy_qty, '->', ret)
            # check trading error
            if ret == 4:
                remain_time = cpStatus.LimitRequestRemainTime
                printlog('Warning: Consecutive order restrict. Waiting time:', remain_time / 1000)
                time.sleep(remain_time / 1000)
                return False
            if ret != 0:
                printlog('Order request error:', str(ret))
                post_message(token, '#stock', 'Order request error: '+str(ret))
                return False
            if rqStatus != 0:
                printlog('Order fail:', rqStatus, errMsg)
                post_message(token, '#stock', 'Order fail: '+str(rqStatus)+', '+str(errMsg)+
                '\nstock: '+str(stock_name)+' '+str(code))
                return False
            time.sleep(2)
            printlog('Possible order price :', buy_amount)
            stock_name, bought_qty = get_stock_balance(code)
            printlog('get_stock_balance :', stock_name, stock_qty)
            if bought_qty > 0:
                bought_list.append(code)
                post_message(token, '#stock', datetime.now().strftime('[%m/%d %H:%M:%S]')+'\n'
                                        "`buy_etf (" + str(stock_name) + ' : ' + str(code) + 
                                        ") -> " + str(bought_qty) + "EA bought!" + "`")
    except Exception as ex:
        post_message(token, '#stock', datetime.now().strftime('[%m/%d %H:%M:%S]')+'\n'
                        "`buy_etf (" + str(code) + ") -> exception! " + str(ex) + "`")


# sell all
def sell_all():
    try:
        cpTradeUtil.TradeInit()
        acc = cpTradeUtil.AccountNumber[0]  # account number
        accFlag = cpTradeUtil.GoodsList(acc, 1)  # -1:total, 1:stock, 2:futures/option
        while True:
            stocks = get_stock_balance('ALL')
            total_qty = 0
            for s in stocks:
                total_qty += s['qty']
            if total_qty == 0:
                return True
            for s in stocks:
                if s['qty'] != 0:
                    cpOrder.SetInputValue(0, "1")  # 1:bid, 2:ask
                    cpOrder.SetInputValue(1, acc)  # account number
                    cpOrder.SetInputValue(2, accFlag[0])
                    cpOrder.SetInputValue(3, s['code'])  # item code
                    cpOrder.SetInputValue(4, s['qty'])
                    cpOrder.SetInputValue(7, "1")  # option >> 0:basic, 1:IOC, 2:FOK
                    cpOrder.SetInputValue(8, "12")
                    ret = cpOrder.BlockRequest()
                    printlog('IOC sell', s['code'], s['name'], s['qty'],
                             '-> cpOrder.BlockRequest() -> returned', ret)
                    if ret == 4:
                        remain_time = cpStatus.LimitRequestRemainTime
                        printlog('Warning: Consecutive order restrict. Waiting time:', remain_time / 1000)
                time.sleep(1)
            time.sleep(30)
    except Exception as ex:
        post_message(token, '#stock', datetime.now().strftime('[%m/%d %H:%M:%S]')+'\n'
                                                "sell_all() -> exception! " + str(ex))

                                    
# end function
def endProgram():
    # you can choose what to end

    # if you want to shut down your computer when trading is finished,
    # use first code and delete second code

    # if you want to just end stock auto trading program,
    # use second code and delete first code


    # os.system('shutdown -s -t 0') # first code: shut down your computer
    sys.exit(0) # second code: end stock auto trader
# End of functions ---------------------------------------------------------------


# main logic
if __name__ == '__main__':
    try:
        # ex) symbol_list = ['A122630', 'A252670']
        # symbol_list is list of target items
        # code will get symbol_list from symbols.txt file

        # you need to fill symbol_list at 'symbols.txt' file-------------
        with open('symbols.txt') as f:
            lines = f.readlines()
            symbol_list = lines[0].split()
        # ---------------------------------------------------------------
        bought_list = []

        # you need to change here by yourself----------------------------
        target_buy_count = 3 # number of items to buy
        buy_percent = 0.33 # (1 / target_buy_count) - commision
        # ---------------------------------------------------------------

        printlog('check_creon_system() :', check_creon_system())  # check creon connection
        stocks = get_stock_balance('ALL')
        total_cash = int(get_current_cash())
        buy_amount = total_cash * buy_percent  # calculate order price
        printlog('Possible order price :', total_cash)
        printlog('Order rate by items :', buy_percent)
        printlog('Order price by items :', buy_amount)
        printlog('Start time :', datetime.now().strftime('%m/%d %H:%M:%S'))
        soldout = False

        while True:
            t_now = datetime.now()
            t_9 = t_now.replace(hour=9, minute=0, second=0, microsecond=0)
            t_start = t_now.replace(hour=9, minute=5, second=0, microsecond=0)
            t_sell = t_now.replace(hour=15, minute=15, second=0, microsecond=0)
            t_exit = t_now.replace(hour=15, minute=20, second=0, microsecond=0)
            today = datetime.today().weekday()
            # sell unsold items before trading start
            if t_9 < t_now < t_start and soldout == False: 
                soldout = True
                sell_all()
            # AM 09:05 ~ PM 03:15 : buy
            if t_start < t_now < t_sell:  
                for sym in symbol_list:
                    if len(bought_list) < target_buy_count:
                        buy_etf(sym)
                        time.sleep(1)
                # send account info at h:30
                if t_now.minute == 30 and 0 <= t_now.second <= 10:
                    get_stock_balance('ALL')
                    time.sleep(10)
            # PM 03:15 ~ PM 03:20 : sell all items
            if t_sell < t_now < t_exit:  
                if sell_all() == True:
                    post_message(token, '#stock', datetime.now().strftime('[%m/%d %H:%M:%S]')+'\n'
                                                '`sell_all() returned True -> self-destructed!`')
                    endProgram()
            if t_exit < t_now:  # PM 03:20 ~ :End program
                post_message(token, '#stock', datetime.now().strftime('[%m/%d %H:%M:%S]')+'\n'
                                                            '`Out of time! Self-destructed!`')
                endProgram()
            time.sleep(3)
    except Exception as ex:
        post_message(token, '#stock', datetime.now().strftime('[%m/%d %H:%M:%S]')+'\n'
                                                '`main -> exception! ' + str(ex) + '`')