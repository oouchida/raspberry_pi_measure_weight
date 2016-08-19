# -*- coding: utf-8 -*- 

import os
import ConfigParser
import json
import gspread
import oauth2client.client
from datetime import datetime as dt

inifile = ConfigParser.SafeConfigParser()
inifile.read("%s/setting.ini" % os.path.dirname(__file__))

private_key_filename = inifile.get("settings","private_key_filename")
DEBUG = inifile.get("settings","debug")

#容器の重さ
offset = inifile.get("settings","offset")

# 認証
json_key = json.load(open(os.path.dirname(__file__) + '/' + private_key_filename))
scope = ['https://spreadsheets.google.com/feeds']
credentials = oauth2client.client.SignedJwtAssertionCredentials(json_key['client_email'], json_key['private_key'].encode(), scope)
gc = gspread.authorize(credentials)

# スプレットシートを開く
ss = gc.open(inifile.get("settings","spreadsheet_name"))

# 今年のシートを開く
tdatetime = dt.now()
try:
	sh = ss.worksheet(tdatetime.strftime("%Y"))
except:
	sh = ss.add_worksheet(tdatetime.strftime("%Y"), rows=5000, cols=10)

# 体重を測る
import weight
w = weight.weight()
w.measure()

if DEBUG:
	print w.date,' ',str(float(w.value) - float(offset))

# 1行ずつ追加する
i = 1
while i <= 5000:
	val = sh.cell(i, 1).value
	if not val:
		sh.update_cell(i, 1, w.date)
		sh.update_cell(i, 2, str(float(w.value) - float(offset)))
		break
	i += 1
