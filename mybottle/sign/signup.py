from bottle import route, run, request
import xml.etree.ElementTree as ET
from time import strftime, localtime, time, clock

from bisect import bisect_left
from xls.xls_record import get_records_from_xls, write_to_excel

mem_dir = '/home/y184zhan/tmp/'
readable = mem_dir+'xml_file.txt'
origin = mem_dir+'msg_file.txt'
KEYWORD = '1python'

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
DATA_INDEX = []
def main():
    global DATA
    global DATA_INDEX
    DATA = read_data_file()
    DATA_INDEX = [x[0] for x in DATA]

def read_data_file():
    filename = './sign_record.xls'

    datalist = get_records_from_xls(filename, 'Clear')
    return datalist

def build_echostr(msg):
    content = msg['Content'].strip()
    welcome =  u"Welcome to Coach Workroom"

    if content == "print" and msg['FromUserName'] == "oPZW5t7_QdCpwjFK092Bn-iywx6s":
        welcome = u"Yes, Sir !\n"
        data_list = [x[4] for x in DATA]
        len_ = len(data_list) - 2
        names = ',\n'.join(data_list)
        welcome += str(len_) + '\n'
        welcome += names

    elif content == "save" and msg['FromUserName'] == "oPZW5t7_QdCpwjFK092Bn-iywx6s":
        welcome = u"Yes, Sir !"
        write_to_excel('result.xls', 'SIGN', len(DATA), 7, None, DATA)

    elif content.lower() == 'update':
        welcome = u"Please type in your ID\n(e.g. 10240148)"
        update_data_clear(msg['FromUserName'])

    elif KEYWORD in content:
        user = update_data_sign(msg['FromUserName'], content, msg['CreateTime'])
        if user: # user[4] == name:
            if user[1]: # meno
                welcome = u"%s, you have signed!" %user[4]
            else:
                welcome = u"Welcome to sign-in: %s" %user[4]
        else:
            welcome = u"Please type in Nokia ID:\n(e.g. 10240148)"

    elif content.isdigit() and len(content) == 8:
        welcome = u"Please type in your name\n(e.g. ZhangYang):"
        update_data_nokiaid(msg['FromUserName'], content)

    elif is_name(content):
        welcome = u"Please type in keyword to sign-in"
        update_data_name(msg['FromUserName'], content)

    else:
        user = update_data_find(msg['FromUserName'])
        if user: # user[4] == name
            if not user[4]: 
                welcome = u"Please type in your name\n(e.g. ZhangYang):"
            elif user[1]: # user[1] == memo
                welcome = u"%s, you have signed!" % user[4]
            else:
                welcome = u"%s, please type in keyword to sign" % user[4]
        else:
            welcome = u"Please sign up with your:\nNokiaID (e.g. 12345678)"

    echostr = textTpl % (msg['FromUserName'], msg['ToUserName'], str(int(time())),
            welcome)

#    #print(DATA)
    return echostr

def is_name(str_):
    return str_.isalpha() and str_[0].isupper()

def update_data_clear(openid):
    index = bisect_left(DATA_INDEX, openid)
    if index < len(DATA_INDEX) and DATA_INDEX[index] == openid:
        DATA[index][4] = ''
        DATA[index][5] = ''

def update_data_find(openid):
    index = bisect_left(DATA_INDEX, openid)
    if index < len(DATA_INDEX) and DATA_INDEX[index] == openid:
        return DATA[index]


def update_data_sign(openid, meno, timestamp):
    global DATA
    global DATA_INDEX

    index = bisect_left(DATA_INDEX, openid)
    if index < len(DATA_INDEX) and DATA_INDEX[index] == openid:
#        print('found openid for ', meno)
        DATA[index][1] = meno
        DATA[index][2] = timestamp

        return DATA[index]
    else:
        new = [openid, meno, '', '', '', '', '']
        DATA.insert(index, new)
        DATA_INDEX.insert(index, openid)
    return

def update_data_name(openid, name):
    global DATA
    global DATA_INDEX

    index = bisect_left(DATA_INDEX, openid)
    if index < len(DATA_INDEX) and DATA_INDEX[index] == openid:
#        print('found openid for ', name)
        if not DATA[index][4].strip():
            DATA[index][4] = name
    else:
        new = [openid, '', '', '', name, '', ' ']
        DATA.insert(index, new)
        DATA_INDEX.insert(index, openid)
        

def update_data_nokiaid(openid, nokiaid):
    global DATA
    global DATA_INDEX

    index = bisect_left(DATA_INDEX, openid)
    if index < len(DATA_INDEX) and DATA_INDEX[index] == openid:
#        print('found openid for ', nokiaid)
        if not DATA[index][5].strip():
            DATA[index][5] = nokiaid
    else:
        new = [openid, '', '', '', '', nokiaid,' ']
        DATA.insert(index, new)
        DATA_INDEX.insert(index, openid)

'''
    user = {'ID':msg['FromUserName'], 'Memo': msg['Content'], 'Name':msg['name'], 
           'Nokia ID':msg['nokiaid'], 'Department':msg['mdep'],
           'TimeStamp':msg['CreateTime'], 'Sign':msg['Content']}

'''
if __name__ == "__main__":
    main()
    run(host='0.0.0.0', port=80)

