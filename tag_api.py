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


def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db

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
# @basic_auth.required
def home():
    return "<h1>tag</p>"

@app.route('/new', methods=['POST'])
@requires_auth
def new():
#adding a tag for an existing article
    auth = request.authorization
    username = auth.username
    
    result = request.json
    new_val = 0

    if 'tag' in result:
        tag = str(result['tag'])
    else:
        return "Error: No tag field provided. Please specify Tags."

    if 'article_title' in result:
        title = result['article_title']
    else:
        return "Error: No article title field provided. Please specify an Article title."

    if 'article_content' in result:
        content = result['article_content']
        new_val = 1


   
    global author


    # connection

    conn = sqlite3.connect('blog.db')

    c = conn.cursor()

    curDate = datetime.datetime.now()

    temp_title = title.replace(" ","%20")

    flag = 0

    if tag.find(',') != -1: 
        tags_list = tag.split(",")
        flag = 1
    else:
        tags_list = tag

    try:

        if new_val == 1:
            c.execute("insert into article (content, title, author, url, createdDate, modifiedDate) values (:content, :title, :author, :url, :createdDate, :modifiedDate)", {'content': content, 'title': title, 'author': author, 'createdDate': str(curDate), 'modifiedDate': str(curDate), 'url': 'http://127.0.0.1:5000/search/' + temp_title})
            
        
        c.execute("select articleId from article where isDeleted = 0 and title = (:title) COLLATE NOCASE", {'title': title})

        result_set = c.fetchone()

        if result_set:
            id = result_set[0]
        else:
            conn.close()
            resp = Response(status=404, mimetype='application/json')
            return resp
    		# return "Article doesn't exist or may have been deleted"

        if flag == 0:
            c.execute("insert into tags (articleId, tag, author, createdDate) values (:articleId, :tag, :author, :createdDate)", {'articleId': id, 'tag': tags_list, 'author': author, 'createdDate': str(curDate)})
        else:
            for ele in tags_list:
	            c.execute("insert into tags (articleId, tag, author, createdDate) values (:articleId, :tag, :author, :createdDate)", {'articleId': id, 'tag': ele, 'author': author, 'createdDate': str(curDate)})
        
        conn.commit()

       
        conn.close()

        resp = Response(status=201, mimetype='application/json')
        resp.headers['location'] = 'http://127.0.0.1:5000/search?title='

      
        
    except sqlite3.Error as e:
        resp = Response(status=409, mimetype='application/json')

    return resp


@app.route('/removeTag', methods=['DELETE'])
@requires_auth
def removeTag():
#adding a tag for an existing article
    auth = request.authorization
    username = auth.username
    
    result = request.json

    if 'tag' in result:
        tag = str(result['tag'])
    else:
        return "Error: No tag field provided. Please specify Tags."

    if 'article_title' in result:
        title = result['article_title']
    else:
        return "Error: No article title field provided. Please specify an Article title."

    print(tag)
    print(title)
    # print(author)
   
    global author


    # connection

    conn = sqlite3.connect('blog.db')

    c = conn.cursor()

    curDate = datetime.datetime.now()

    flag = 0

    if tag.find(',') != -1: 
        tags_list = tag.split(",")
        flag = 1
    else:
        tags_list = tag

    try:
	
        c.execute("select articleId from article where isDeleted = 0 and title = (:title) COLLATE NOCASE", {'title': title})

        result_set = c.fetchone()

        if result_set:
            id = result_set[0]
        else:
            conn.close()
            resp = Response(status=404, mimetype='application/json')
            return resp
    		# return "Article doesn't exist or may have been deleted"

        print(id)
        print(flag)
        print(tags_list)
        print(title)
        print(author)




        if flag == 0:
            c.execute("""update tags set isDeleted = 1 
            where articleId = (:articleId) and tag = (:tag) 
            and author = (:author)""", {'articleId': id, 'tag': tags_list, 'author': author})
        else:
            for ele in tags_list:
	            c.execute("""update tags set isDeleted = 1 
                where articleId = (:articleId) and tag = (:tag) 
                and author = (:author)""", {'articleId': id, 'tag': ele, 'author': author})
        
        conn.commit()

       
        conn.close()

        resp = Response(status=200, mimetype='application/json')
        # resp.headers['location'] = 'http://127.0.0.1:5000/search?title='
        # return resp

      
        
    except sqlite3.Error as e:
        resp = Response(status=409, mimetype='application/json')

    return resp


@app.route('/searchTag/<title>', methods=['GET'])
def searchTag(title):
#get all tags for a specific title

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
    	
    conn.row_factory = dict_factory
    c = conn.cursor()
  
    c.execute("select tag from tags where isDeleted = 0 and articleId = (:id)", {'id': id})

    result = jsonify(c.fetchall())

    if result is None:
        resp = Response(status=404, mimetype='application/json')
       	return resp

    conn.close()
    

    return result

@app.route('/searchArticle/<tag>', methods=['GET'])
def searchArticle(tag):
#get all articles for a specific tag

    if tag =='':
        return "Error: No tag field provided. Please specify Tag to get the articles"

    # connection
   

    conn = sqlite3.connect('blog.db')
    conn.row_factory = dict_factory
    c = conn.cursor()
    c.execute("select title from article where isDeleted = 0 and articleId in (Select articleId from tags where tag = (:tag) COLLATE NOCASE)", {'tag': tag})

    result_set = c.fetchall()

       
    if result_set is None:
       	resp = Response(status=404, mimetype='application/json')
       	return resp

    conn.close()
    

    return jsonify(result_set)



app.run()