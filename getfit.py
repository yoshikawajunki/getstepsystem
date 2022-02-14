import os
import json
import httplib2
import requests
import gspread
import json
import numpy as np
import slack     #https://blog.imind.jp/entry/2020/03/07/231631
import datetime
import schedule

import time
from datetime import datetime, timedelta
from apiclient.discovery import build
from oauth2client.client import OAuth2WebServerFlow, flow_from_clientsecrets
from oauth2client.file import Storage


OAUTH_SCOPE = 'https://www.googleapis.com/auth/fitness.activity.read'
DATA_SOURCE = "derived:com.google.step_count.delta:com.google.android.gms:estimated_steps"
REDIRECT_URI = 'urn:ietf:wg:oauth:2.0:oob'

#スプレッドシート操作始まり

#ServiceAccountCredentials：Googleの各サービスへアクセスできるservice変数を生成します。
from oauth2client.service_account import ServiceAccountCredentials

#2つのAPIを記述しないとリフレッシュトークンを3600秒毎に発行し続けなければならない
scope = ['https://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/drive']

#認証情報設定
#ダウンロードしたjsonファイル名をクレデンシャル変数に設定（秘密鍵、Pythonファイルから読み込みしやすい位置に置く）
credentials_GSpread = ServiceAccountCredentials.from_json_keyfile_name('renkei_spreadsheet.json', scope)

#OAuth2の資格情報を使用してGoogle APIにログインします。
gc = gspread.authorize(credentials_GSpread)

#共有設定したスプレッドシートキーを変数[SPREADSHEET_KEY]に格納する。
#DB用
SPREADSHEET_KEY = '$$$$$$$$$$$$$$$$$$_$$$$$$$$$$$$$$$$_$$$$$$$$'#シート名

#共有設定したスプレッドシートを指定
#DB用
workbook = gc.open_by_key(SPREADSHEET_KEY)

#スプレッドシートの中のワークシート名を直接指定
worksheet = workbook.worksheet('歩数')


#スプレッドシート操作終わり



def auth_data(CREDENTIALS_FILE):#コピペ

    credentials = ""
    
    credentials = Storage(CREDENTIALS_FILE).get()
    
    # Create an httplib2.Http object and authorize it with our credentials
    http = httplib2.Http()
    http = credentials.authorize(http)

    fitness_service = build('fitness', 'v1', http=http)

    return fitness_service


def retrieve_data(fitness_service, dataset):

    return fitness_service.users().dataSources(). \
        datasets(). \
        get(userId='me', dataSourceId=DATA_SOURCE, datasetId=dataset). \
        execute()


def nanoseconds(nanotime):#コピペ
    """
    ナノ秒に変換する
    """
    dt = datetime.fromtimestamp(nanotime // 1000000000)
    return dt.strftime('%Y-%m-%d %H:%M:%S')


def logwrite(date, step):#コピペ
    with open('./data/step.log', 'a') as outfile:
        outfile.write(str(date) + "," + str(step) + "\n")


def Run(CREDENTIAL,row,col):#最終行以外コピペ
    if __name__ == "__main__":

        authdata = auth_data(CREDENTIAL)

        # 前日分のデータを取得
        TODAY = datetime.today() - timedelta(days=1)
        STARTDAY = datetime(TODAY.year, TODAY.month, TODAY.day, 0, 0, 0)
        NEXTDAY = datetime(TODAY.year, TODAY.month, TODAY.day, 23, 59, 59)
        NOW = datetime.today()

        START = int(time.mktime(STARTDAY.timetuple())*1000000000)
        NEXT = int(time.mktime(NEXTDAY.timetuple())*1000000000)
        END = int(time.mktime(NOW.timetuple())*1000000000)
        data_set = "%s-%s" % (START, NEXT)

        while True:

            if END < NEXT:
                break

            dataset = retrieve_data(authdata, data_set)

            starts = []
            ends = []
            values = []
            for point in dataset["point"]:
                if int(point["startTimeNanos"]) > START:
                    starts.append(int(point["startTimeNanos"]))
                    ends.append(int(point["endTimeNanos"]))
                    values.append(point['value'][0]['intVal'])

            print("Steps:{}".format(sum(values)))

            step = sum(values)

            startdate = STARTDAY.date()
            logwrite(startdate, step)

            STARTDAY = STARTDAY + timedelta(days=1)
            NEXTDAY = NEXTDAY + timedelta(days=1)
            START = int(time.mktime(STARTDAY.timetuple())*1000000000)
            NEXT = int(time.mktime(NEXTDAY.timetuple())*1000000000)
            data_set = "%s-%s" % (START, NEXT)

            #スプレッドシートの自分の場所に書き込む
            worksheet.update_cell(row, col, sum(values))

def job():
  rowlengths =1 + len(worksheet.col_values(1) )#一列目の「あ」が何個あるかで行の長さ（日付）を取得する。
  
  #別ファイルに保存してあるcredentialファイル(アクセスキー)を使って歩数データを取得する。また、取得した後に、最終行の次の行の各ユーザーの欄に歩数を記録してゆく。 
  Run("./secret/credentials",rowlengths,3)#
  Run("./secret/credentials_aa",rowlengths,4)#さん
  Run("./secret/credentials_bb",rowlengths,5)#君
  Run("./secret/credentials_cc",rowlengths,6)#君
  Run("./secret/credentials_s",rowlengths,7)#
  Run("./secret/credentials_y",rowlengths,8)#
  Run("./secret/credentials_h",rowlengths,9)#
  Run("./secret/credentials_s",rowlengths,10)#
  Run("./secret/credentials_m",rowlengths,11)#
  Run("./secret/credentials_b",rowlengths,12)#
  Run("./secret/credentials_sh",rowlengths,13)#
  Run("./secret/credentials_i",rowlengths,14)#
  Run("./secret/credentials_f",rowlengths,15)#
  Run("./secret/credentials_s",rowlengths,16)#
  Run("./secret/credentials_ki",rowlengths,17)#
  Run("./secret/credentials_s",rowlengths,18)#
  Run("./secret/credentials_n",rowlengths,19)#
  Run("./secret/credentials_sa",rowlengths,20)#
  Run("./secret/credentials_z",rowlengths,21)#
  Run("./secret/credentials_w",rowlengths,22)#わ
  Run("./secret/credentials_a",rowlengths,23)#

  #以下、歩数を降順にしてslackに投稿

  #全員の名簿を配列として取ってくる。
  memberlist = worksheet.row_values(4)
  #余分な最初の２つを削除
  memberlist.pop(0)
  memberlist.pop(0)

  print(memberlist)

  #全員の歩数を配列として取ってくる。
  steplist = worksheet.row_values(rowlengths)
  #余分な最初の2つの列を削除
  steplist.pop(0)
  steplist.pop(0)

  #降順処理を行うためにstr型からint型へと変換
  steplist_int= [int(s) for s in steplist]

  #memberlistとsteplist_intを合わせて二次元配列にする。
  list = []
  list = [(memberlist[i],steplist_int[i]) for i in range(0, len(steplist_int), 1)]

  #steplist_intに注目してソート（降順）
  list = sorted(list, reverse=True, key=lambda x: x[1]) 

  #評価をslackに通知するプログラム始まり
  OAUTH_TOKEN = 'xoxb-1997033449121-1978769063270-A9MR6m1XagfuZnWcUaZ5c4od' 
  CHANNEL_NAME = '#general'
  client = slack.WebClient(token=OAUTH_TOKEN)

  response = client.chat_postMessage(
  channel=CHANNEL_NAME,
  text=
  "昨日の歩数（敬称略）" + "\n" +
    list[0][0] +":" +str(list[0][1]) + "\n" +
    list[1][0] +":" +str(list[1][1]) + "\n" +
    list[2][0] +":" +str(list[2][1]) + "\n" +
    list[3][0] +":" +str(list[3][1]) + "\n" +
    list[4][0] +":" +str(list[4][1]) + "\n" +
    list[5][0] +":" +str(list[5][1]) + "\n" +
    list[6][0] +":" +str(list[6][1]) + "\n" +
    list[7][0] +":" +str(list[7][1]) + "\n" +
    list[8][0] +":" +str(list[8][1]) + "\n" +
    list[9][0] +":" +str(list[9][1]) + "\n" +
    list[10][0] +":" +str(list[10][1]) + "\n" +
    list[11][0] +":" +str(list[11][1]) + "\n" +
    list[12][0] +":" +str(list[12][1]) + "\n" +
    list[13][0] +":" +str(list[13][1]) + "\n" +
    list[14][0] +":" +str(list[14][1]) + "\n" +
    list[15][0] +":" +str(list[15][1]) + "\n" +
    list[16][0] +":" +str(list[16][1]) + "\n" + 
    list[17][0] +":" +str(list[17][1]) + "\n" +
    list[18][0] +":" +str(list[18][1]) + "\n" +
    list[19][0] +":" +str(list[19][1]) + "\n" +
    list[20][0] +":" +str(list[20][1]) 
    )
  #評価をslackに通知するプログラム終わり

  #歩数を降順にしてslackに投稿終わり



  #1列目にまた新たな「あ」を加える。
  worksheet.update_cell(rowlengths, 1, "あ")






def oshirase(bunnshou):#GoogleFit同期催促用
  OAUTH_TOKEN = 'xoxb-1997033449121-1978769063270-A9MR6m1XagfuZnWcUaZ5c4od' 
  CHANNEL_NAME = '#おしらせ'
  client = slack.WebClient(token=OAUTH_TOKEN)
  response = client.chat_postMessage(
  channel=CHANNEL_NAME,
  text=bunnshou
  )

def asa():
 oshirase("おはようございます！\n アプリの同期を行ってください\n（Mii fit→(ヘルスケア)→Google fit）")

def yoru():
  oshirase("こんばんは！\n アプリの同期を行ってください！\n（Mii fit→(ヘルスケア)→Google fit）\n昨日の歩数はこの後10時半に発表されます！")  







schedule.every().day.at("22:30").do(job)
schedule.every().day.at("10:00").do(asa)
schedule.every().day.at("21:35").do(yoru)


while True:#定期実行のため
  schedule.run_pending()
  time.sleep(60)