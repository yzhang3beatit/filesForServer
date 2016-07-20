# coding=utf-8
# reserved by Nokia
#
#

try:
    import xlrd
    import xlwt
except:
    print('3rd party package needed: xlrd xlwt')
import time
import datetime
import os
import xml.etree.ElementTree as ET

def sec2str(secs):
    return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(secs))

def parse_xml(msgstr):
    root = ET.fromstring(msgstr)
    print(msgstr)
    msg = {}
    for child in root:
        if child.tag == 'CreateTime':
            msg[child.tag] = sec2str(int(child.text))
        else:
            msg[child.tag] = child.text

    msg['name'] = ''
    msg['nokiaid'] = 0
    msg['mdep'] = ''
    return msg

def split_xml(xmls):
    start = 0
    end = 0
    ret = []
    start = xmls.find('<xml>')
    while end != -1:
        end = xmls.find('<xml>', start + 1)
        if end == -1:
            break
        ret.append(xmls[start:end])
        start = end if end != -1 else start
    
    ret.append(xmls[start:])
    return ret

def fetch_messages_with_keyword(messages):
    i = 0
    users = []
    for message in split_xml(messages):
        user = fetch_msg_from_message(message)
        if same_id_exists(user, users):
            users = merge_user_msg(user, users)
        else:
            users.append(user)
    print_list(users)
    return users

def same_id_exists(user, user_list):
    for usr in user_list:
        if usr['ID'] == user['ID']:
            return True
    return False

def merge_user_msg(user, user_list):
    for i, usr in enumerate(user_list):
        if usr['ID'] == user['ID']:
            user_list[i]['Memo'] = user['Memo']
            user_list[i]['TimeStamp'] = user['TimeStamp']
            user_list[i]['Sign'] = user['Name']

            user_list[i]['Nokia ID'] = user['Nokia ID'] if user['Nokia ID'] else user_list[i]['Nokia ID']
            user_list[i]['Department'] = user['Department'] if user['Department'] else user_list[i]['Department']
            user_list[i]['Name'] = user['Name'] if user['Name'] else user_list[i]['Name']
            break
    return user_list


def fetch_msg_from_message(message):
    msg = parse_xml(message)
    user = {'ID':msg['FromUserName'], 'Memo': msg['Content'], 'Name':msg['name'], 
           'Nokia ID':msg['nokiaid'], 'Department':msg['mdep'],
           'TimeStamp':msg['CreateTime'], 'Sign':msg['Content']}
    return user


def record_messages_with_keyword(filenam, messages, keyword):
    row_list = get_records_from_xls(filenam, 'Clear')
    print_list(row_list)
    newname = os.path.dirname(filenam) + '/' + get_cur_time() + '_' + os.path.basename(filenam)

    if messages:
        msgs = fetch_messages_with_keyword(messages)
    else:
        msgs = []

    combine_record_with_history(newname, keyword, len(row_list), Columns['Max'], msgs, row_list)


Columns = {}
Columns['ID'] = 0
Columns['Memo'] = 1
Columns['TimeStamp'] = 2
Columns['Department'] = 3
Columns['Name'] = 4
Columns['Nokia ID'] = 5
Columns['Sign'] = 6
Columns['Max'] = 7


def combine_record_with_history(newname, keyword, nrows, ncols, messages, alist):
    row_list = []
    msgs = []
    found = 'N'
    print('alist', alist)
    for li in alist:
        hist_id = li[Columns['ID']]
        if li[Columns['TimeStamp']] != 'TimeStamp':
            li[Columns['TimeStamp']] = ''
        for msg in messages:
            WeChat_id = msg['ID']
            if (WeChat_id == hist_id) or (li[Columns['Nokia ID']] == int(msg['Nokia ID'])):
                print('found', msg['Name'], WeChat_id,) 
                print(hist_id, li[Columns['Nokia ID']], int(msg['Nokia ID']))
                li[Columns['ID']] = msg['ID']
                li[Columns['Memo']] = msg['Memo']
                li[Columns['TimeStamp']] = msg['TimeStamp']
                if msg['Department']:
                    li[Columns['Department']] = msg['Department']
                li[Columns['Name']] = msg['Name']
                if msg['Nokia ID'] != '0':
                    li[Columns['Nokia ID']] = msg['Nokia ID']
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
            print('not found:', msg)
            msgs = combine_record_in(msgs, msg)


    print('msgs_list:', msgs)
    print('row_list:', row_list)
    write_to_excel(newname, keyword, nrows, ncols, msgs, row_list)

def combine_record_in(msgs, record):
#    found = 'N'
#   for msg in msgs:
#        if (msg['ID'] == record['ID']) or (int(msg['Nokia ID']) == int(record['nokia ID'])):
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
        for type in ['ID', 'Memo', 'TimeStamp', 'Department', 'Name', 'Nokia ID', 'Sign']:
            write_to_cell(sheet, 0, Columns[type], type)
        row = row + 1
    if not msgs:
        return

    for msg in msgs:
        print('write to sheet', row, msg)
        write_message_to_row(sheet, msg, row)
        row = row + 1

def write_message_to_row(sheet, msg, row):
    for key in msg.keys():
        write_to_cell(sheet, row, Columns[key], msg[key])

def write_to_cell(sheet, row, col, value):
    sheet.write(row, col, value)


def get_cur_time():
    mkd = datetime.date
    year = time.localtime(time.time()).tm_year
    month = time.localtime(time.time()).tm_mon
    day = time.localtime(time.time()).tm_mday

    return mkd(year, month, day).strftime("%Y-%m-%d")

def print_list(list):
    for li in list:
        print(li)

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
            ids = get_ids_from(line)
            ids = clear_ids(ids, keyword)
            messages = get_msgs_from(ids, keyword)
            print_list(messages)
            break
    return messages

def get_ids_from(line):
    line = line.decode('utf-8')
    lines = line.split('{')
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
        if key_matched(key, keyword):
            continue
        cont = get_content_from(id)
        name = get_name_from(id)
        Nokiaid = get_nokiaid_from(id)
        dep = get_department_from(id)
        date = get_date_time_from(id)
        wxid = 'ID'+get_weixingid_from(id)
        msg = {'ID':wxid, 'Memo': cont, 'Name':name, 'Nokia ID':nokiaid, 'Department':dep,
               'TimeStamp':date, 'Sign':name}
        msgs.append(msg)
    return msgs

def get_weixingid_from(id):
    start = id.find('openid')
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


def get_Nokiaid_from(id):
    cont = get_content_from(id)
    Nokiaid = cont.split(';')
    if len(Nokiaid) > 1 and nokiaid[1].isdigit():
        return Nokiaid[1]
    else:
        return '0'


def get_department_from(id):
    cont = get_content_from(id)
    Nokiaid = cont.split(';')
    if len(Nokiaid) > 2 and nokiaid[2].lower().startswith('d'):
        return Nokiaid[2].upper()
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
        if data[0] != 'OpenID' and filter == 'Clear':
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
            row_list = get_list_from_sheet(sh, flag)
        else:
            print('no sheet in %s' % (fromf))
    except Exception as e:
        print('no file %s' % fromf)
        row_list = [['Weixing signature',' ',' ',' ',' ',' ',' '],['OpenID', 'Memo', 'TimeStamp', 'Department', 'Name',
        'Nokia ID', ' ']]
        write_to_sheet(fromf, 'default', row_list)
    print("row: %d, \tcolume: %d in %s" % (nrows, ncols, fromf))

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
                if sum[Columns['Name']] == '':
                    sum[Columns['Name']] = row[Columns['Name']]
                sum.append(row[Columns['Sign']])
                break
        if found == 'Y':
            found = 'N'
        else:
            new_list = add_record_in_xls(new_list, row)
    print('new sign adding in list:')
    print_list(new_list)
    print('end')
    new_list = add_unmatched_record(new_list, sum_list)
#        new_list.append(sum)
    return new_list

def matched_row(sum, sign):
    is_match = False
    if sum[Columns['Name']] != '' and sign[Columns['Name']] != '':
        is_match = (sum[Columns['Name']] == sign[Columns['Name']])
#    elif sum[Columns['Nokia ID']] != '0' and sign[Columns['nokia ID']] != 'NSN ID':
#        is_match = (int(sum[Columns['Nokia ID']]) == int(sign[Columns['nokia ID']]))
    return is_match

def add_record_in_xls(new_list, row):
    print('Adding new in sum record:')
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
    print('write to %s' % filename)


if __name__ == "__main__":
    filename = './sign_record.xls'
    fromfile = './sign_record.xls'
    tofile = './VSP_sign_records.xls'
    date = '10:10'
    
#    combine_sign_xls(tofile, fromfile)
#    print get_content_from(pri_id)
#    fetch_messages_with_keyword(messages)
#    fetch_msg_from_message(msg)
#    print fetch_Nokiaid_from( u'KISSvTAS;69003924;D2;YiXiaoLong')
#    fetch_openid_from_msg(msg)
#    fetch_remark_name_from_msg(msg)
#    print fetch_date_from_msg(date)
#    fetch_sign_from_msg(msg)
#    get_messages_from(lines, 'KISSvTAS')
    with open('/home/y184zhan/tmp/msg_file.txt', 'br') as f:
        lines = f.read()
#    print_list(lines)
    line = lines
    print(type(line))
    print(line)
    record_messages_with_keyword(filename, line.decode(), 'KISS_LAN')

