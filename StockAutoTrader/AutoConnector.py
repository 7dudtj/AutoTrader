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

    'AutoConnector.py' will let you automatically login to 'CREON PLUS' program.
    This program works correctly only when you already installed CREON PLUS program on your computer.

    This program only runs on Windows by 32bit python.
    Your computer's OS must be Windows, and you have to run this program at 32bit python.

    Warning! This program is not developed yet.
"""

# import modules
from pywinauto import application
from datetime import datetime
import os, time, sys


# check if today is Sat or Sun
today = datetime.today().weekday()
if today == 5 or today == 6:
    sys.exit(0)


# os operation
os.system('taskkill /IM coStarter* /F /T')
os.system('taskkill /IM CpStart* /F /T')
os.system('taskkill /IM DibServer* /F /T')
os.system('wmic process where "name like \'%coStarter%\'" call terminate')
os.system('wmic process where "name like \'%CpStart%\'" call terminate')
os.system('wmic process where "name like \'%DibServer%\'" call terminate')
time.sleep(5)


# get id, pwd, and pwdcert

# you need to fill id, pwd, and pwdcert at 'keys.txt' file-------
with open('keys.txt') as f:
    lines = f.readlines()
    id = lines[0].strip() # line 1: id
    pwd = lines[1].strip() # line 2: pwd
    pwdcert = lines[2].strip() # line 3: pwdcert
# --------------------------------------------------------------- 


# start CREON
app = application.Application()
app.start(f'C:\CREON\STARTER\coStarter.exe /prj:cp '
          f'/id:{id} /pwd:{pwd} /pwdcert:{pwdcert} /autostart')
time.sleep(60)
