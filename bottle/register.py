from bottle import route, run, static_file, request, response, template

@route('/')
def home():
    return static_file('index.html', root='.')

@route('/echo/?<thing>')
def echo(thing):
    return "Say hello to my little friend: %s!" % thing

# url /register?id=1&page=5
@route('/register')
def register():
    register_id = request.query.id
    page = request.query.page or '1'
    return template('Register ID: {{id}} (page {{page}})', id=register_id, page=page)

#    return ''' <form method = "POST">
#                 <input name="name" type="text"/>
#                 <input name="password" type="password"/>
#                 <input type="submit" value="Login"/>
#                 </form>'''

run(host="localhost", port=80)
