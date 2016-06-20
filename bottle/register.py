# -*- coding: utf-8 -*-


from bottle import route, get, run, static_file, request, response, template, HTTPResponse
import time
import hashlib

@route('/')
def home():
    return static_file('index.html', root='.')

@route('/echo/?<thing>')
def echo(thing):
    return "Say hello to my little friend: %s!" % thing

# url /register?id=1&page=5
@route('/weixin')
def register():
    signature = request.query.signature
    timestamp = request.query.timestamp
    nonce = request.query.nonce
    echostr = request.query.echostr
    token = "zhangyang2"
    print(signature, timestamp, nonce, echostr)
    lists = [token, timestamp, nonce]
    lists.sort()
    data = ""
    for s in lists:
        data += s

    sha1 = hashlib.sha1()
    sha1.update(data.encode("utf8"))
#    map(sha1.update, lists)
    hashcode = sha1.hexdigest()
    print(hashcode)
    
    if hashcode == signature:
        return HTTPResponse(echostr)

#    return template('Register ID: {{id}} (page {{page}})', id=signature, page=nonce)

#    return ''' <form method = "POST">
#                 <input name="name" type="text"/>
#                 <input name="password" type="password"/>
#                 <input type="submit" value="Login"/>
#                 </form>'''

@get('/')
def index():
    print(request.GET.get('echostr'))
    return request.GET.get('echostr')
run(host="172.19.0.1", port=80)
