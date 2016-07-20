from bottle import route, run, request
import xml.etree.ElementTree as ET
from time import strftime, localtime, time, clock

from xls.xls_record import get_records_from_xls, write_to_excel

mem_dir = '/home/y184zhan/tmp/'
readable = mem_dir+'xml_file.txt'
origin = mem_dir+'msg_file.txt'

def sec2str(secs):
    return strftime("%Y-%m-%d %H:%M:%S", localtime(secs))

def parseXML(recvmsg):
#    printToFile(recvmsg, origin, 'ba')
    _str = byte2str(recvmsg)
#    printToFile(_str, readable, 'a+')

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
    echostr = build_echostr(msg)

    end = clock()
    print('Running time: %fs' %(end - start))
    return echostr

DATA = []
def main():
    global DATA
    DATA = read_data_file()
    print(DATA)
    '''
    msg = {"FromUserName":"adfadsfaisdfjalsdifja", "ToUserName":"adfasdfasdf", "Content":"61340148"}
    print(build_echostr(msg))
    print(DATA)
    msg = {"FromUserName":"adfadsfaisdfjalsdifja", "ToUserName":"adfasdfasdf", "Content":"ZhangYang"}
    print(build_echostr(msg))
    print(DATA)
    msg = {"FromUserName":"adfadsfaisdfjalsdifja", "ToUserName":"adfasdfasdf", "Content":"save"}
    print(build_echostr(msg))
    print(DATA)
    '''

def read_data_file():
    filename = './sign_record.xls'

    datalist = get_records_from_xls(filename, 'Clear')
    return datalist

def build_echostr(msg):
    content = msg['Content']
    welcome =  u"Welcome to Coach Workroom"
    if content == "save":
        write_to_excel('result.xls', 'SIGN', len(DATA), 7, None, DATA)

    elif '1python' in content:
        name = update_data_sign(msg['FromUserName'], content)
        welcome = u"Welcome to sign-in: %s" %name

    elif content.isdigit() and len(content) == 8:
        welcome = u"Please type in your name:"
        update_data_nokiaid(msg['FromUserName'], content)

    elif is_name(content):
        welcome = u"Welcome to sign-up"
        update_data_name(msg['FromUserName'], content)

    else:
        welcome = u"Please type in your Nokia ID:"

    echostr = textTpl % (msg['FromUserName'], msg['ToUserName'], str(int(time())),
            welcome)

    return echostr

def is_name(str_):
    return str_.isalpha() and str_[0].isupper()

def update_data_sign(openid, meno):
    found = False
    global DATA
    print('DATA:', DATA)
    for i, data_ in enumerate(DATA):
        print('data_: ', data_)
        if data_[0] == openid:
            found = True
            print('found openid for ', meno)
            return DATA[i][4]
    if not found:
        new = [openid, meno, '', '', '', '', '']
        DATA.append(new)
    return

def update_data_name(openid, name):
    found = False
    global DATA
    print('DATA:', DATA)
    for i, data_ in enumerate(DATA):
        print('data_: ', data_)
        if data_[0] == openid:
            found = True
            print('found openid for ', name)
            if not data_[4].strip():
                DATA[i][4] = name
    if not found:
        new = [openid, '', '', '', name, '', ' ']
        DATA.append(new)

def update_data_nokiaid(openid, nokiaid):
    found = False
    global DATA
    print('DATA:', DATA)
    for i, data_ in enumerate(DATA):
        print('data_: ', data_)
        if data_[0] == openid:
            found = True
            print('found openid for ', nokiaid)
            if not data_[5].strip():
                DATA[i][5] = nokiaid
    if not found:
        new = [openid, '', '', '', '', nokiaid,' ']
        DATA.append(new)

'''
    user = {'ID':msg['FromUserName'], 'Memo': msg['Content'], 'Name':msg['name'], 
           'Nokia ID':msg['nokiaid'], 'Department':msg['mdep'],
           'TimeStamp':msg['CreateTime'], 'Sign':msg['Content']}

'''
if __name__ == "__main__":
    main()
    run(host='0.0.0.0', port=80)

