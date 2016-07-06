#!-*-encoding:utf-8-*-
import requests
import json
import time
from bottle import route, run, request

def do_update_access_token():
    url = "https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid=wxf7f3f4bbb813d30f&secret=e90ab10f431ed93cf45b01e2d7f46af1"
    print("GET %s" % url)

    resp = requests.get(url)
    print(resp.status_code)
    print(resp.headers)
    print()
    jsonData = json.loads(resp.text)
    try:
        print("access_token: ", jsonData["access_token"])
        print("expires_in: ", jsonData["expires_in"])
    except:
        return None, None
    
    return jsonData["access_token"], jsonData["expires_in"]

def cal_time_period(start_time):
    current_time = time.time()
    diff = current_time - start_time
    print(current_time, diff)
    return diff

def update_access_token():
    token, expires = do_update_access_token()
    while token is None:
        time.sleep(10)

        if expires is None:
            expires = 10


        token, expires = do_update_access_token()
    return token

def runs():
    start_time = time.time()
    token = update_access_token()
    run_time = cal_time_period(start_time)

@route('/', method='POST')
def msg_post():
    for l in request.body:
        print(l)

runs()
#run(host="0.0.0.0", port=80)
