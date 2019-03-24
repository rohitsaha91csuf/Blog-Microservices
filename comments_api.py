import flask
from flask import request, jsonify, json
from flask import Response
import datetime
import sqlite3
from functools import wraps
import hashlib


app = flask.Flask(__name__)
app.config["DEBUG"] = True

author = ''

DATABASE = 'blog.db'


def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d

# app.config['BASIC_AUTH_USERNAME'] = 'john'
# app.config['BASIC_AUTH_PASSWORD'] = 'matrix'

# basic_auth = BasicAuth(app)

# class check(BasicAuth):
#     def check_credentials(username, password):
#         return true

def check_auth(username, password):
    """This function is called to check if a username /
    password combination is valid.
    """
    conn = sqlite3.connect('blog.db')

    c = conn.cursor()

    c.execute("Select password from user where name = (:username) and isDeleted=0", {"username": username})

    pswd = c.fetchone()

    if pswd is None:
        return False

    pswd = str(pswd[0])
    db_password = hashlib.md5(password.encode())
    db_password = str(db_password.hexdigest())    
    # pswd = pswd[0]

    print(pswd)
    print(db_password)


    if pswd is not None:
        return pswd == db_password
    


    # return username == 'john' and password == 'matrix'

def authenticate():
    """Sends a 401 response that enables basic auth"""
    # return "invalid"

    resp = Response(status=404, mimetype='application/json')


    return resp

def auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        global author
        if not auth or not check_auth(auth.username, auth.password):
            author = 'Anonymous Coward'
        else:
            author= auth.username
        return f(*args, **kwargs)
    return decorated

def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth or not check_auth(auth.username, auth.password):
            return authenticate()
        global author 
        author= auth.username
        return f(*args, **kwargs)
    return decorated


@app.route('/', methods=['GET'])
def home():
    return "<h1>Comments API</p>"

@app.route('/new', methods=['POST'])
@auth
def new():

    result = request.json

    if 'comment' in result:
        comment = result['comment']
    else:
        return "Error: No comment field provided. Please specify comment."

    if 'title' in result:
        title = result['title']
    else:
        return "Error: No title field provided. Please specify an title."

    # if 'author' in result:
    #     author = result['author']
    # else:
    #     return "Error: No author field provided. Please specify an author."
    global author

    # connection

    try:

        conn = sqlite3.connect('blog.db')

        c = conn.cursor()

        curDate = datetime.datetime.now()

        c.execute("select articleId from article where isDeleted = 0 and title = (:title) COLLATE NOCASE", {'title': title})

        result_set = c.fetchone()

        if result_set:
            id = result_set[0]
        else:
            conn.close()
            resp = Response(status=404, mimetype='application/json')
            # return "Article doesn't exist or may have been deleted"
            return resp


        

        # for row in result_set:
        #     id = row["articleId"]
        

        c.execute("insert into comments (articleId, comment, author, createdDate) values (:id, :comment,  :author, :createdDate)", {'id': id, 'comment': comment, 'title': title, 'author': author, 'createdDate': str(curDate)})
        
        conn.commit()

        c.execute("select * from comments where isDeleted= 0")

        print(c.fetchall())

        conn.close()

        resp = Response(status=201, mimetype='application/json')

    except sqlite3.Error as e:

        resp = Response(status=409, mimetype='application/json')

    # resp = Response(js, status=200, mimetype='application/json')
    # resp.headers['Link'] = 'http://'

    # return "Comment Created"
    return resp

    
@app.route('/delete', methods=['DELETE'])
@requires_auth
def delete():


    # if 'id' in request.args:
    #     id = request.args['id']
    # else:
    #     return "Error: No id field provided. Please specify id of the article."

    # connection

    result = request.json

    if 'id' in result:
        id = result['id']
    else:
        return "Error: No ID field provided. Please specify ID."

    try:


        conn = sqlite3.connect('blog.db')

        c = conn.cursor()

        c.execute("""update comments
            set isDeleted = 1
            where isDeleted = 0 and commentId = (:id) and (author = (:author) OR author = 'Anonymous Coward')""", {'id': id, 'author': author})


        conn.commit()

        # c.execute("select * from comments where isDeleted= 0")

        # print(c.fetchall())

        conn.close()

        resp = Response(status=200, mimetype='application/json')

    except sqlite3.Error as e:

        resp = Response(status=409, mimetype='application/json')

    return resp

@app.route('/count/<title>', methods=['GET'])
def count(title):

    if title == '':
        return "Error: No title field provided. Please specify title of the article."

    # connection

    conn = sqlite3.connect('blog.db')

    c = conn.cursor()

    

    c.execute("select articleId from article where isDeleted = 0 and title = (:title) COLLATE NOCASE", {'title': title})

    result_set = c.fetchone()

    if result_set:
        id = result_set[0]
    else:
        conn.close()
        resp = Response(status=404, mimetype='application/json')
        # return "Article doesn't exist or may have been deleted"
        return resp

    c.execute("""
        select count(commentid) from comments
        where articleId= (:id) and isDeleted = 0""", {"id":id})

    commentsCount = c.fetchone()
    commentsCount = str(commentsCount[0])

    conn.close()

    return "Number of comments for given article:" + commentsCount

@app.route('/retrieve/<title>/<num>', methods=['GET'])
def retrieve(title, num):

    # if 'number' in request.args:
    #     num = request.args['number']
    # else:
    #     num = -1

    # if 'title' in request.args:
    #     title = request.args['title']
    # else:
    #     return "Error: No title field provided. Please specify title of the article."


    # connection

    conn = sqlite3.connect('blog.db')
    
    c = conn.cursor()

    c.execute("select articleId from article where isDeleted = 0 and title = (:title) COLLATE NOCASE", {'title': title})

    result_set = c.fetchone()

    if result_set:
        id = result_set[0]
    else:
        conn.close()
        resp = Response(status=404, mimetype='application/json')
        return resp
        # return "Article doesn't exist or may have been deleted"

    conn.row_factory = dict_factory
    c = conn.cursor()

    if num is -1:

        c.execute("SELECT comment FROM comments where isDeleted = 0 and articleId = (:id) ORDER BY commentId DESC", {"id": id})

    else:
        c.execute("""
            
            SELECT comment FROM comments where isDeleted = 0 and articleId = (:id) ORDER BY commentId DESC LIMIT (:number)
            ;""", {'number': num, "id":id})

    result = jsonify(c.fetchall())

    conn.close()

    return result



app.run()

