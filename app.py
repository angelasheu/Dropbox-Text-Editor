import bottle
import pystache2
from bottle import *
from dropbox import *

APP_KEY = 'zadqraqhwfhzreh'
APP_SECRET = 'm6vjijuq3mq41y3'
ACCESS_TYPE = 'app_folder'
TOKEN_STORE = {}


app = Bottle()

def get_session():
    return session.DropboxSession(APP_KEY, APP_SECRET, ACCESS_TYPE)

def get_client(access_token):
    sess = get_session()
    sess.set_token(access_token.key, access_token.secret)
    return client.DropboxClient(sess)


@route('/test')
def test():
    return 'hi'
@post('/submission')
def submission():
    request_token_key = request.query.oauth_token
    if not request_token_key:
        access_token = TOKEN_STORE[accesstoken]
    else:
        sess = get_session()
        request_token = TOKEN_STORE[request_token_key]
        access_token = sess.obtain_access_token(request_token)
        global accesstoken
        accesstoken = access_token.key
        TOKEN_STORE[access_token.key] = access_token
    data = bottle.request.params
    client = get_client(access_token)
    client.put_file(data.path, data.filetext, overwrite=True, parent_rev=data.parent_rev)
    return redirect('/viewfiles')

@get('/')
def login():
    sess = get_session()
    request_token = sess.obtain_request_token()
    TOKEN_STORE[request_token.key] = request_token
    callback = "http://%s/viewfiles" % (bottle.request.headers['host'])
    url = sess.build_authorize_url(request_token, oauth_callback=callback)
    prompt = """Click this <a href="%s">login link</a> to go to Dropbox!"""
    #return prompt % url 
    return pystache2.render_file('home.mustache', {'url': url})

@route('/viewfiles')
def viewfile():
    return viewfiles()
    
@route('/viewfiles/<path:path>')
def viewfiles(oauth_token=None, path='.'):
    request_token_key = request.query.oauth_token
    if not request_token_key:
        access_token = TOKEN_STORE[accesstoken]
    else:
        sess = get_session()
        request_token = TOKEN_STORE[request_token_key]
        access_token = sess.obtain_access_token(request_token)
        global accesstoken
        accesstoken = access_token.key
        TOKEN_STORE[access_token.key] = access_token
    #print 'Token store 1: ' + str(TOKEN_STORE)
    #print 'Access token key: ' + str(access_token.key)
        access_token = TOKEN_STORE[access_token.key]
    client = get_client(access_token)
    context = client.metadata(path)
    if context['is_dir']:
        return pystache2.render_file('viewfiles.mustache', context)
    else:
        f = client.get_file_and_metadata(path)[0].read()
        metadata = client.get_file_and_metadata(path)[1]
        return pystache2.render_file('viewsinglefile.mustache', {'content': f, 'rev': metadata['rev'], 'path': path})
run(host='localhost', port=8080, debug=True)
