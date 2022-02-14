#このファイルで行えること。
#ファイルを実行すると、アクセスコード発行のためのURLが発行されます。そのURLを各ユーザーに踏んでもらって、操作をしてもらい、コードをコピーして打ち込むと、アクセスキーが入ったファイルが作成されます。
#ユーザーが行う操作は「アクセスキー取得の方法.pdf」にまとめてあるので、参考にしてください。
#ちなみに僕はancondaでやってました。

import os
import json
import httplib2
import requests

import time
from datetime import datetime, timedelta
from apiclient.discovery import build
from oauth2client.client import OAuth2WebServerFlow, flow_from_clientsecrets
from oauth2client.file import Storage

OAUTH_SCOPE = 'https://www.googleapis.com/auth/fitness.activity.read'
DATA_SOURCE = "derived:com.google.step_count.delta:com.google.android.gms:estimated_steps"
REDIRECT_URI = 'urn:ietf:wg:oauth:2.0:oob'
CREDENTIALS_FILE = "./secret/credentials"

credentials = ""


#flow = OAuth2WebServerFlow(CLIENT_ID, CLIENT_SECRET, OAUTH_SCOPE, REDIRECT_URI)
flow = flow_from_clientsecrets(
# API有効化時に取得したOAuth用のJSONファイルを指定
'./secret/oauth2.json',
# スコープを指定
scope=OAUTH_SCOPE,
# ユーザーの認証後の、トークン受け取り方法を指定（後述）
redirect_uri=REDIRECT_URI)

authorize_url = flow.step1_get_authorize_url()
print('下記URLをブラウザで起動してください。')
print(authorize_url)

code = input('Codeを入力してください: ').strip()
credentials = flow.step2_exchange(code
)

#if not os.path.exists(CREDENTIALS_FILE):(ここでcredentialファイルが空だった場合保存することになっているがなぜかエラーが出るため、消す)
Storage(CREDENTIALS_FILE).put(credentials)

# Create an httplib2.Http object and authorize it with our credentials
http = httplib2.Http()
http = credentials.authorize(http)

fitness_service = build('fitness', 'v1', http=http)

print(fitness_service)