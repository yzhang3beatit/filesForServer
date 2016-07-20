#!-*-encoding:utf-8-*-
import requests
import json
import time
from bottle import route, run, request

def do_add_new_menu(access_token):
    url = "https://api.weixin.qq.com/cgi-bin/menu/create?access_token=%s"
    new_menu = {"button":[
        {
            "type":"view",
            "name":"Submit",
            "url":"http://yzhang3.cn/login"
        },
        {
            "name":"Feedback",
            "sub_button":[
            {
                "type":"click",
                "name":"Best",
                "key":"5"
                    
            },
            {
                "type":"click",
                "name":"Better",
                "key":"4"

            },
            {
                "type":"click",
                "name":"Normal",
                "key":"3"

            },
            {
                "type":"click",
                "name":"bad",
                "key":"2"

            },
            {
                "type":"click",
                "name":"Worse",
                "key":"1"

            }]

        }]
    }

    url = url % access_token

    print("POST %s" % url)
    resp = requests.post(url, data=new_menu)
    print(resp.status_code)
    print(resp.headers)
    print(resp.text)
    '''
    jsonData = json.loads(resp.text)
    try:
        print("access_token: ", jsonData["access_token"])
        print("expires_in: ", jsonData["expires_in"])
    except:
        return None, None
    
    return jsonData["access_token"], jsonData["expires_in"]
    '''

def cal_time_period(start_time):
    current_time = time.time()
    diff = current_time - start_time
    print(current_time, diff)
    return diff

def add_new_menu():
    access_token = fetch_access_token()
    do_add_new_menu(access_token)

def fetch_access_token():
    with open('./access_token.txt', 'rb') as f:
        return f.read().decode()

def runs():
    start_time = time.time()
    token = add_new_menu()
    run_time = cal_time_period(start_time)

runs()
#run(host="0.0.0.0", port=80)
