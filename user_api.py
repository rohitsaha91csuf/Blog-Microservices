import flask
from flask import request, jsonify, json, Response, g
import datetime
import sqlite3
from functools import wraps
#from flask_basicauth import BasicAuth
import hashlib


app = flask.Flask(__name__)
app.config["DEBUG"] = True

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
def home():
    return "<h1>testing user at default GET method</h1><p>This site is a prototype API for distant reading of science fiction novels.</p>"

@app.route('/new', methods=['POST'])
def new():


    result = request.json

    if 'name' in result:
        name = result['name']
    else:
        return "Error: No name field provided. Please specify a name."

    if 'emailid' in result:
        emailid = result['emailid']
    else:
        return "Error: No emailid field provided. Please specify an emailid."

    if 'password' in result:
        password = result['password']
        db_password = hashlib.md5(password.encode())
	
    else:
        return "Error: No password field provided. Please specify a password."
    


    # connection

    conn = sqlite3.connect('blog.db')

    c = conn.cursor()

    curDate = datetime.datetime.now()	

    try:


        c.execute("insert into user (emailid, name, password, createdDate, modifiedDate) values (:emailid, :name, :password, :createdDate, :modifiedDate)", {'emailid': emailid, 'name': name, 'password': str(db_password.hexdigest()), 'createdDate': str(curDate), 'modifiedDate': str(curDate)})
        
        conn.commit()

        c.execute("select * from user")

        print(c.fetchall())

        conn.close()

        resp = Response(status=201, mimetype='application/json')

    except sqlite3.Error as e:
        resp = Response(status=409, mimetype='application/json')


    return resp

# @app.route('/meta', methods=['GET'])
# def meta():

#     # connection

#     conn = sqlite3.connect('blog.db')

#     c = conn.cursor()

#     c.execute("SELECT * FROM user")

#     result = jsonify(c.fetchall())

#     conn.close()

#     return result

@app.route('/delete', methods=['DELETE'])
@requires_auth
def delete():

    # if 'emailid' in request.args:
    #     emailid = request.args['emailid']
    # else:
    #     return "Error: No emailid field provided."

    # if 'password' in request.args:
    #     password = request.args['password']
	# db_password = hashlib.md5(password.encode())
    # else:
    #     return "Error: No password field provided."

    auth = request.authorization
    username = auth.username

    # connection

    try:


        conn = sqlite3.connect('blog.db')

        c = conn.cursor()

        # c.execute("""select 1 from user
        #     where isDeleted = 0 and emailid = (:emailid) """, {'emailid': emailid })

        # count = c.fetchone()

        # if count == 1 :   
        c.execute("""update user set isDeleted = 1 where isDeleted = 0 and name = (:username)""", {'username': username })
            # flag = 1

        # else:
            # flag = 0

        conn.commit()
        conn.close()


        # if flag == 1:
        resp = Response(status=200, mimetype='application/json')

    except sqlite3.Error as e:
        resp = Response(status=404, mimetype='application/json')
            
    # else:
    #     resp = Response(status=404, mimetype='application/json')
	    
    return resp



@app.route('/update', methods=['PATCH'])
@requires_auth
def update():

    # if 'emailid' in request.args:
    #     emailid = request.args['emailid']
    # else:
    #     return "Error: No emailid field provided."

    # if 'oldpassword' in request.args:
    #     oldpassword = request.args['oldpassword']
	# db_oldpassword = hashlib.md5(oldpassword.encode())
    # else:
    #     return "Error: No oldpassword field provided."

    auth = request.authorization
    username = auth.username

    result = request.json

    if 'newpassword' in result:
        newpassword = result['newpassword']
        db_newpassword = hashlib.md5(newpassword.encode())
    else:
        return "Error: No newpassword field provided."

    # connection

    try:

        conn = sqlite3.connect('blog.db')

        c = conn.cursor()
            
        # c.execute("""select 1 from user
        #     where isDeleted = 0 and emailid = (:emailid) and password = (:oldpassword)""", {'emailid': emailid , 'oldpassword':str(db_oldpassword.hexdigest())})

        # count = c.fetchone()
        
        # if count == 1:
        c.execute("""update user
            set password = (:newpassword)
                where isDeleted = 0 and name = (:username)""", {'username': username , "newpassword" : str(db_newpassword.hexdigest())})
        # flag = 1
        # else:
        # flag = 0


        conn.commit()
        conn.close()


        # if flag == 1:
        # return "updated"
        # else:
        # return "this data combination does not exists"

        resp = Response(status=200, mimetype='application/json')
    
    except sqlite3.Error as e:
        resp = Response(status=404, mimetype='application/json')

    return resp



app.run()
