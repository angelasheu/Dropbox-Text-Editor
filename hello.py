from bottle import route, run
from dropbox import session

@route('/hello')
def hello():
    return "Hello World!"

run(host='localhost', port=8080, debug=True)
