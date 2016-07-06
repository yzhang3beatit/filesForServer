from bottle import route, run, request
import xml.etree.ElementTree as ET
from time import strftime, localtime, time, clock

mem_dir = '/home/y184zhan/tmp/'
readable = mem_dir+'xml_file.txt'
origin = mem_dir+'msg_file.txt'

def sec2str(secs):
    return strftime("%Y-%m-%d %H:%M:%S", localtime(secs))

def parseXML(recvmsg):
    printToFile(recvmsg, origin, 'ba')
    _str = byte2str(recvmsg)
    printToFile(_str, readable, 'a+')

    root = ET.fromstring(_str)
    msg = {}
    for child in root:
        if child.tag == 'CreateTime':
            msg[child.tag] = sec2str(int(child.text))
        else:
            msg[child.tag] = child.text
    return msg

textTpl = '''<xml>
<ToUserName><![CDATA[%s]]></ToUserName>
<FromUserName><![CDATA[%s]]></FromUserName>
<CreateTime>%s</CreateTime>
<MsgType><![CDATA[text]]></MsgType>
<Content><![CDATA[%s]]></Content>
</xml>'''

def printToFile(msg, filepath, flag):
    f = open(filepath, flag)
    f.write(msg)
    f.close()

def byte2str(utfByte):
    _str = utfByte.decode()
#    print(_str)
    return _str


@route('/', method='POST')
def index():
    start = clock()
    openid = request.query.openid
#    print("OPENID in FORMS:", openid)
#    for l in request.body:
#        print(l)
    msg = parseXML(request.body.read())
    echostr = textTpl % (msg['FromUserName'], msg['ToUserName'], str(int(time())),
            u"Welcome to Coach Workroom")
#    print(echostr)
    end = clock()
    print('Running time: %fs' %(end - start))
    return echostr


run(host='0.0.0.0', port=80)
