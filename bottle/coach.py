# coding=utf-8
# reserved by Nokia
#
#

try:
    import xlrd
    import xlwt
except:
    print '3rd party package needed: xlrd xlwt'
import time
import datetime
import os


def fetch_messages_with_keyword(messages):
    i = 0
    users = []
    start = messages.find('<ul id="listContainer"')
    messages = messages[start+len('<ul id="listContainer"'):]
    while start != -1:
#        print messages
        start = messages.find('<li data-id')
        end = messages.find('</li>')
        if start == -1:
            break
        user = fetch_msg_from_message(messages[start:end])
        users.append(user)
        start = messages.find('<li data-id')
        i = i + 1
        messages = messages[end+len('</li>'):]
    print 'total:', i
    print_list(users)
    return users

def fetch_msg_from_message(message):
    fakeid = fetch_fakeid_from_msg(message)
    fakeid = 'ID'+fakeid
    name = fetch_remark_name_from_msg(message)
    date = fetch_date_from_msg(message)
    sign = fetch_sign_from_msg(message)
    nsnid = fetch_nsnid_from(sign)
    dep = fetch_department_from(sign)

    user = {'ID':fakeid, 'Memo': sign, 'Name':name, 'NSN ID':nsnid, 'Department':dep,
            'TimeStamp':date, 'Sign':name}
    print user
    return user

def fetch_nsnid_from(sign):
    nsnid = sign.split(';')
    if len(nsnid) > 1 and nsnid[1].isdigit():
        return nsnid[1]
    else:
        return '0'


def fetch_department_from(sign):
    nsnid = sign.split(';')
    if len(nsnid) > 2 and nsnid[2].lower().startswith('d'):
        return nsnid[2].upper()
    else:
        return ''


def fetch_sign_from_msg(message):
    sign = fetch_label_from_msg(message, 'class="wxMsg "').strip()
    for i in [',', '.', ':', u'：', u'。', u'，', u'；']:
        sign = sign.replace(i, ';')
    return sign



def fetch_remark_name_from_msg(message):
    return fetch_label_from_msg(message, 'class="remark_name"')

def fetch_label_from_msg(msg, key):
    start = msg.find(key)
    msg = msg[start:]

    start = msg.find('>')
    msg = msg[start+1:]
    end = msg.find('<')

    return msg[:end]


def fetch_date_from_msg(message):
    date = fetch_label_from_msg(message, 'class="message_time"')
#    date = message
    today = datetime.date.today()
    yesterday = today - datetime.timedelta(days=1)
    if len(date) > 7:
        start = date.find(' ')
        date = yesterday.strftime('%Y-%m-%d') + date[start:]
    else:
        date = today.strftime('%Y-%m-%d ') + date
    return date
#    return getdate(date_time)

def fetch_fakeid_from_msg(message):
    start = message.find('data-tofakeid')
    return fetch_data_from_msg(message[start:])

def fetch_data_from_msg(message):
    start = message.find('"')
    end = message[start+1:].find('"')
    end = end + start + 2
    return message[start+1:end-1]

def record_messages_with_keyword(filenam, messages, keyword):
    row_list = get_records_from_xls(filenam, 'Clear')
    print_list(row_list)
    newname = os.path.dirname(filenam) + '/' + get_cur_time() + '_' + os.path.basename(filenam)

    if messages:
        msgs = fetch_messages_with_keyword(messages)
#        msgs = get_messages_from(messages, keyword)
    else:
        msgs = []

    combine_record_with_history(newname, keyword, len(row_list), Columns['Max'], msgs, row_list)
#    print row_list


Columns = {}
Columns['ID'] = 0
Columns['Memo'] = 1
Columns['TimeStamp'] = 2
Columns['Department'] = 3
Columns['Name'] = 4
Columns['NSN ID'] = 5
Columns['Sign'] = 6
Columns['Max'] = 7


def combine_record_with_history(newname, keyword, nrows, ncols, messages, alist):
    row_list = []
    msgs = []
    found = 'N'
    for li in alist:
        hist_id = li[Columns['ID']]
        if li[Columns['TimeStamp']] != 'TimeStamp':
            li[Columns['TimeStamp']] = ''
        for msg in messages:
            WeChat_id = msg['ID']
            if (WeChat_id == hist_id) or (li[Columns['NSN ID']] == int(msg['NSN ID'])):
                print 'found', msg['Name'], WeChat_id, 
                print hist_id, li[Columns['NSN ID']], int(msg['NSN ID'])
                li[Columns['ID']] = msg['ID']
                li[Columns['Memo']] = msg['Memo']
                li[Columns['TimeStamp']] = msg['TimeStamp']
                if msg['Department']:
                    li[Columns['Department']] = msg['Department']
                li[Columns['Name']] = msg['Name']
                if msg['NSN ID'] != '0':
                    li[Columns['NSN ID']] = msg['NSN ID']
                li[Columns['Sign']] = msg['Sign']
        row_list.append(li)

    for msg in messages:
        WeChat_id = msg['ID']
        for li in row_list:
            hist_id = li[Columns['ID']]
            if WeChat_id == hist_id:
                found = 'Y'
                break
        if found == 'Y':
            found = 'N'
        else:
            print 'not found:', msg
            msgs = combine_record_in(msgs, msg)


    write_to_excel(newname, keyword, nrows, ncols, msgs, row_list)

def combine_record_in(msgs, record):
#    found = 'N'
#   for msg in msgs:
#        if (msg['ID'] == record['ID']) or (int(msg['NSN ID']) == int(record['NSN ID'])):
#            found = 'Y'
#    if found == 'N':
    msgs.append(record)
    return msgs

def write_to_excel(filename, sheetname, nrows, ncols, content, row_list):
    wbk = xlwt.Workbook()
    sheet = wbk.add_sheet(sheetname, True)

    for row in range(nrows):
        for col in range(ncols):
            write_to_cell(sheet, row, col, row_list[row][col])

    if nrows:
        row = row + 1
        write_message_to_rows(sheet, content, row)
    else:
        write_message_to_rows(sheet, content, 0)
    wbk.save(filename)

def write_message_to_rows(sheet, msgs, row):
    if row == 0:
        for type in ['ID', 'Memo', 'TimeStamp', 'Department', 'Name', 'NSN ID', 'Sign']:
            write_to_cell(sheet, 0, Columns[type], type)
        row = row + 1


    for msg in msgs:
        write_message_to_row(sheet, msg, row)
        row = row + 1

def write_message_to_row(sheet, msg, row):
    for key in msg.keys():
        write_to_cell(sheet, row, Columns[key], msg[key])

def write_to_cell(sheet, row, col, value):
#    ezxf = xlwt.easyxf
#    if type(value) == type('') and not value.isdigit():
    sheet.write(row, col, value)
#    else:
#        sheet.write(row, col, int(value), ezxf(num_format_str='#######0'))
    print row, col, value


def get_cur_time():
    mkd = datetime.date
    year = time.localtime(time.time()).tm_year
    month = time.localtime(time.time()).tm_mon
    day = time.localtime(time.time()).tm_mday

    return mkd(year, month, day).strftime("%Y-%m-%d")

def print_list(list):
    for li in list:
        print li

def open_html():
    fp = open('./html.txt', 'r')
    lines = fp.readlines()

    return lines


def get_messages_from(html, keyword):
    messages = []
    lines = html.split('\n')
    print_list(lines)
    for line in lines:
        line = line.strip()
        if line.startswith('list'):
            print 'line:', len(line)
            ids = get_ids_from(line)
            print 'ids:', ids
            ids = clear_ids(ids, keyword)
            messages = get_msgs_from(ids, keyword)
            print_list(messages)
            break
    return messages

def get_ids_from(line):
    line = line.decode('utf-8')
    lines = line.split('{')
    print 'ids_line:'
    print_list(lines)
    ids = []
    for li in lines:
        if li.startswith('"id"'):
            ids.append(li)
    return ids


def key_matched(long_key, key):
    return not long_key.upper().startswith(key.upper())

def clear_ids(ids, keyword):
    ret = []
    for i in range(len(ids)):
        key = get_keyword_from(ids[i])
        if key_matched(key, keyword):
            continue
        if id_not_exists(ids[i], ret):
            ret.append(ids[i])
    return ret

def id_not_exists(id, ids):
    wxid = get_weixingid_from(id)
    for i in ids:
        ii = get_weixingid_from(i)
        if wxid == ii:
            return False

    return True

def get_msgs_from(ids, keyword):
    msgs = []
    for id in ids:
        key = get_keyword_from(id)
        print key, keyword
        if key_matched(key, keyword):
            continue
        cont = get_content_from(id)
        name = get_name_from(id)
        nsnid = get_nsnid_from(id)
        dep = get_department_from(id)
        date = get_date_time_from(id)
        wxid = 'ID'+get_weixingid_from(id)
        print wxid
        msg = {'ID':wxid, 'Memo': cont, 'Name':name, 'NSN ID':nsnid, 'Department':dep,
               'TimeStamp':date, 'Sign':name}
        msgs.append(msg)
    return msgs

def get_weixingid_from(id):
    start = id.find('fakeid')
    end = id.find(',"nick_name')
    wxid = id[start:end]
    start = wxid.find(':"')
    return wxid[start+2:-1]


def get_name_from(id):
    start = id.find('remark_name')
    end = id.find(',"has_reply')
    name_opt = id[start:end]
    start = name_opt.find(':"')
    return name_opt[start+2:-1]

def get_keyword_from(id):
    cont = get_content_from(id)
    kw = cont.split(';')
    if len(kw) > 0:
        return kw[0].replace(' ', '')
    else:
        return ''


def get_nsnid_from(id):
    cont = get_content_from(id)
    nsnid = cont.split(';')
    if len(nsnid) > 1 and nsnid[1].isdigit():
        return nsnid[1]
    else:
        return '0'


def get_department_from(id):
    cont = get_content_from(id)
    nsnid = cont.split(';')
    if len(nsnid) > 2 and nsnid[2].lower().startswith('d'):
        return nsnid[2].upper()
    else:
        return ''

def get_content_from(id):
    start = id.find('content')
    end = id.find(',"source')
    name_opt = id[start:end]
    start = name_opt.find(':"')
    cont = name_opt[start+2:-1]
    for i in [',', '.', ':', u'：', u'。', u'，', u'；']:
        cont = cont.replace(i, ';')
    return cont

def get_date_time_from(id):
    start = id.find('date_time')
    end = id.find(',"content')
    name_opt = id[start:end]
    start = name_opt.find(':')
    return getdate(name_opt[start+1:])

def getdate(date_time):
    x = time.localtime(float(date_time))
    return time.strftime("%Y-%m-%d %H:%M:%S", x)



def get_list_from_sheet(sheet, filter=''):
    nrows = sheet.nrows
    row_list = []
    for row in range(nrows):
        data = sheet.row_values(row)
        if row != 0 and filter == 'Clear':
            data[len(data) - 1] = ''
            data[Columns['Memo']] = ''
        if filter == 'Signed' and data[len(data) - 1] == '':
            continue

        row_list.append(data)

    return row_list


def get_records_from_xls(fromf, flag=''):
    nrows = 0
    ncols = 0
    try:
        bk = xlrd.open_workbook(fromf)
        shnames = bk.sheet_names()
        if len(shnames):
            sh = bk.sheet_by_name(shnames[0])
            nrows = sh.nrows
            ncols = sh.ncols
        else:
            print 'no sheet in %s' % (fromf)
    except:
        print 'no file %s' % fromf
    print "nrows %d, \tncols %d: \t%s" % (nrows, ncols, fromf)
    row_list = get_list_from_sheet(sh, flag)

    return row_list

def combine_sign_xls(tofile, fromf):

    newname = os.path.dirname(tofile) + '/' + get_cur_time() + '_' + os.path.basename(tofile)

    row_list = get_records_from_xls(fromf, 'Signed')
#    print_list(row_list)

    sum_list = get_records_from_xls(tofile)
 #   print_list(sum_list)
    sum_list = append_title(sum_list)
    new_list = combine_records_in_xls(row_list, sum_list)
#    print_list(new_list)

    write_to_sheet(newname, 'sum', new_list)

def append_title(sum_list):
    sum_list[1].append(get_cur_time())
    return sum_list

def combine_records_in_xls(row_list, sum_list):
    new_list = []
    new_list.append(sum_list[1])
    found = 'N'
    for row in row_list:
        if row[Columns['Name']] == 'Name':
            continue
        for si in range(len(sum_list)):
            sum = sum_list[si]
            if sum[Columns['Name']] == 'Name':
                continue
            if matched_row(sum, row):
                found = 'Y'
                print 'Found:', row[Columns['Sign']]
                if sum[Columns['Name']] == '':
                    sum[Columns['Name']] = row[Columns['Name']]
                sum.append(row[Columns['Sign']])
                break
        if found == 'Y':
            found = 'N'
        else:
            new_list = add_record_in_xls(new_list, row)
    print 'new sign adding in list:'
    print_list(new_list)
    print 'end'
    new_list = add_unmatched_record(new_list, sum_list)
#        new_list.append(sum)
    return new_list

def matched_row(sum, sign):
    is_match = False
    if sum[Columns['Name']] != '' and sign[Columns['Name']] != '':
        is_match = (sum[Columns['Name']] == sign[Columns['Name']])
#    elif sum[Columns['NSN ID']] != '0' and sign[Columns['NSN ID']] != 'NSN ID':
#        is_match = (int(sum[Columns['NSN ID']]) == int(sign[Columns['NSN ID']]))
    return is_match

def add_record_in_xls(new_list, row):
    print 'Adding new in sum record:'
    print_list(row)
    new_list.append(row)
    new_list = align_last_sign(new_list)
    return new_list

def align_last_sign(new_list):
    length = len(new_list[0])
    for i in range(length - len(new_list[-1])):
        new_list[-1].insert(len(new_list[-1]) - 1, '')

    return new_list

def get_length_in_sum(sum_list):
    length = 0
    for sum in sum_list:
        if length < len(sum):
            length = len(sum)

    return length

def add_unmatched_record(new_list, sum_list):
    length = get_length_in_sum(sum_list)
    for si in range(len(sum_list)):
        sum = sum_list[si]
        if len(sum) < length:
            for i in range(length - len(sum)):
                sum.append('')

    for li in range(len(new_list)):
        if li > 0:
            sum_list.append(new_list[li])
    return sum_list

def write_to_sheet(filename, sheetname, row_list):
    wbk = xlwt.Workbook()
    sheet = wbk.add_sheet(sheetname, True)

    for rowi in range(len(row_list)):
        for coli in range(len(row_list[rowi])):
            sheet.write(rowi, coli, row_list[rowi][coli])
    wbk.save(filename)
    print 'write to %s' % filename


if __name__ == "__main__":
    filename = './sign_record.xls'
    fromfile = './sign_record.xls'
    tofile = './VSP_sign_records.xls'
    date = '10:10'
    msg = '<li data-id="206045409" id="msgListItem206045409" class="message_item replyed"> <div class="message_opr"> <a title="收藏消息" starred="" idx="206045409" action="search" class="js_star icon18_common star_gray" href="javascript:;">取消收藏</a> <a title="快捷回复" class="icon18_common reply_gray js_reply" data-tofakeid="30094145" data-id="206045409" href="javascript:;">快捷回复</a> </div> <div class="message_info"> <div class="message_status"><em class="tips">已回复</em></div> <div class="message_time">09:29</div> <div class="user_info"> <a class="remark_name" data-id="206045409" data-fakeid="30094145" target="_blank" href="/cgi-bin/singlesendpage?tofakeid=30094145&amp;t=message/send&amp;action=index&amp;token=1381246310&amp;lang=zh_CN">Wu Tianle</a> <span data-id="206045409" data-fakeid="30094145" class="nickname">(<strong>5天_IT.Will</strong>)</span> <a style="display:none;" title="修改备注" data-fakeid="30094145" class="icon14_common edit_gray js_changeRemark" href="javascript:;"></a> <a data-id="206045409" data-fakeid="30094145" class="avatar" href="/cgi-bin/singlesendpage?tofakeid=30094145&amp;t=message/send&amp;action=index&amp;token=1381246310&amp;lang=zh_CN" target="_blank"> <img data-fakeid="30094145" src="/misc/getheadimg?token=1381246310&amp;fakeid=30094145&amp;msgid=206045409" /> </a> </div> </div> <div class="message_content text"> <div class="wxMsg" data-id="206045409" id="wxMsg206045409">KISSvTAS</div> </div> <div class="js_quick_reply_box quick_reply_box" id="quickReplyBox206045409"> <label class="frm_label" for="">快速回复:</label> <div class="emoion_editor_wrp js_editor"></div> <div class="verifyCode"></div> <p class="quick_reply_box_tool_bar"> <span data-id="206045409" class="btn btn_primary btn_input"> <button data-fakeid="30094145" data-id="206045409" class="js_reply_OK">发送</button> </span><a href="javascript:;" data-id="206045409" class="js_reply_pickup btn btn_default pickup">收起</a> </p> </div>'
    lines = '''
     <li data-id="206045409" id="msgListItem206045409" class="message_item replyed"> <div class="message_opr"> <a title="收藏消息" starred="" idx="206045409" action="search" class="js_star icon18_common star_gray" href="javascript:;">取消收藏</a> <a title="快捷回复" class="icon18_common reply_gray js_reply" data-tofakeid="30094145" data-id="206045409" href="javascript:;">快捷回复</a> </div> <div class="message_info"> <div class="message_status"><em class="tips">已回复</em></div> <div class="message_time">09:29</div> <div class="user_info"> <a class="remark_name" data-id="206045409" data-fakeid="30094145" target="_blank" href="/cgi-bin/singlesendpage?tofakeid=30094145&amp;t=message/send&amp;action=index&amp;token=1381246310&amp;lang=zh_CN">Wu Tianle</a> <span data-id="206045409" data-fakeid="30094145" class="nickname">(<strong>5天_IT.Will</strong>)</span> <a style="display:none;" title="修改备注" data-fakeid="30094145" class="icon14_common edit_gray js_changeRemark" href="javascript:;"></a> <a data-id="206045409" data-fakeid="30094145" class="avatar" href="/cgi-bin/singlesendpage?tofakeid=30094145&amp;t=message/send&amp;action=index&amp;token=1381246310&amp;lang=zh_CN" target="_blank"> <img data-fakeid="30094145" src="/misc/getheadimg?token=1381246310&amp;fakeid=30094145&amp;msgid=206045409" /> </a> </div> </div> <div class="message_content text"> <div class="wxMsg" data-id="206045409" id="wxMsg206045409">KISSvTAS</div> </div> <div class="js_quick_reply_box quick_reply_box" id="quickReplyBox206045409"> <label class="frm_label" for="">快速回复:</label> <div class="emoion_editor_wrp js_editor"></div> <div class="verifyCode"></div> <p class="quick_reply_box_tool_bar"> <span data-id="206045409" class="btn btn_primary btn_input"> <button data-fakeid="30094145" data-id="206045409" class="js_reply_OK">发送</button> </span><a href="javascript:;" data-id="206045409" class="js_reply_pickup btn btn_default pickup">收起</a> </p> </div>
        '''
    pri_id = '"id":205824480,"type":1,"fakeid":"1000580904","nick_name":"薇","date_time":1425549654,"content":"TAS：61328015：D7：Huang Weiwei","source":"","msg_status":4,"remark_name":"Huang Weiwei","has_reply":1,"refuse_reason":"","multi_item":[],"to_uin":3082392893,"send_stat":{"total":0,"succ":0,"fail":0}}'
    messages = '''

    '''
    
    combine_sign_xls(tofile, fromfile)
#    print get_content_from(pri_id)
#    fetch_messages_with_keyword(messages)
#    fetch_msg_from_message(msg)
#    print fetch_nsnid_from( u'KISSvTAS;69003924;D2;YiXiaoLong')
#    fetch_fakeid_from_msg(msg)
#    fetch_remark_name_from_msg(msg)
#    print fetch_date_from_msg(date)
#    fetch_sign_from_msg(msg)
#    get_messages_from(lines, 'KISSvTAS')
#    record_messages_with_keyword(filename, lines, 'KISS_LAN')

