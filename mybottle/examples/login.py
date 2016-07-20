import bottle

def check_login(username, password):
    if username == '123' and password == '234':
        return True
    else:
        return False

def is_number(uchar):
    if uchar >= u'\u0030' and uchar <= u'\u0039':
        return True
    else:
        return False

def is_alpabet(uchar):
    if (uchar >= u'\u0041' and uchar <= u'\u005a') or (uchar >= u'\u0061' and uchar <= u'\u007a'):
        return True
    else:
        return False

def isalpnum(string):
    for s in string:
        if not (is_number(s) or is_alpabet(s) or s.isspace()):
            return False
    return True
            

@bottle.route('/login')
def login():
    return '''<form action="/login" method="post">
                <label style="font-size:40px;">Nokia ID:</lable><input name="Nokia ID" type="text"
                style="height:50px;font-size:40px" size=8/>
                </br>Name:    <input name="Name" type="text" style="height:50px;font-size:40px"/>
                </br>Department: <select name="Department" id="select_k1" class="xla_k"
                style="height:50px;font-size:40px">
                  <option value="SCM">SCM</option>
                  <option value="SWTA">SWTA</option>
                  <option value="O&M">O&M</option>
                  </select>
                </br><input value="Submit" type="submit" style="height:50px;font-size:40px">
              </form>
           '''
@bottle.route('/login', method='POST')
def do_login():
    postValue = bottle.request.POST.decode('utf-8')
    nokiaid = postValue.get('Nokia ID').strip()
    name = postValue.get('Name').strip()
    department = bottle.request.POST.get('Department').strip()

    print(nokiaid)
    print(name)
    print(department)
    

    if not nokiaid.isdigit():
        return "<p>Hello %s,<br/>&nbsp&nbspPlease type in correct Nokia ID: %s</p>" % (name,
                nokiaid)
    if not isalpnum(name):
        return "<p>Hello %s,<br/>&nbsp&nbspPlease type in correct name</p>" % (name)

    return "<p>Hello %s,<br/>&nbsp&nbspThank you for your information.</p>" % name

bottle.run(host='0.0.0.0', port=80)
