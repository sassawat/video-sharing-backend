from flask import Flask, jsonify, request, send_file
from passlib.hash import pbkdf2_sha256 as sha256
import mysql.connector
import datetime

app = Flask(__name__)

config = {
    "user": "root", 
    "password": "123456", 
    "host": "10.0.253.241", 
    "port": 9988, 
    "database": "video_sharing"
    }

try:
    cnx = mysql.connector.connect(**config)
except mysql.connector.Error as err:
    if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
        print("Something is wrong with your user name or password")
    elif err.errno == errorcode.ER_BAD_DB_ERROR:
        print("Database does not exist")
    else:
        print(err)
else:
    print ("Connect database successed.")
    cursor = cnx.cursor()

def get_data_in_format(sql, args):
    res = ''
    data = []
    if args == '':
        cursor.execute(sql)
        for row in cursor:
            res = {
                'id': row[0],
                'username': row[1],
                'password': row[2],
                'firstName': row[3],
                'lastName': row[4],
                'token': row[5],
            }
            data.append(res)
        return data
    else:
        cursor.execute(sql, args)
        for row in cursor:
            res = {
                'id': row[0],
                'username': row[1],
                'password': row[2],
                'firstName': row[3],
                'lastName': row[4],
                'token': row[5],
            }
        return res

@app.route('/api')
def hello_world():
    return jsonify({"api": ["/videos", "/video", "/watch", "/search", "/users", "/user", "/user/authentication"]})

@app.route('/videos')
def videos():   
    data = []

    cursor.execute("SELECT * FROM videos")

    for row in cursor:
        res = {
            'id': row[0],
            'name': row[1],
            'album': row[2],
            'artist': row[3],
            'duration': str(row[4]),
            'description': row[5],
            'path': row[6],
            'privilege': row[7],
        }
        data.append(res)
    # cursor.close()

    return jsonify(data)

@app.route('/video', methods=['GET', 'POST', 'PUT','DELETE'])
def video():
    data = []

    if request.method == "GET":
        id = request.args['id']

        cursor.execute("SELECT * FROM videos WHERE id=%s" %(id))

        for row in cursor:
            res = {
                'id': row[0],
                'name': row[1],
                'album': row[2],
                'artist': row[3],
                'duration': str(row[4]),
                'description': row[5],
                'path': row[6],
                'privilege': row[7],
            }
            data.append(res)
        
        return jsonify(data)
            
    if request.method == "POST":
        _data = request.json
        sql = """INSERT INTO `videos`(`id`, `name`, `album`, `artist`, `duration`, `description`, `path`, `privilege`)
                VALUES (NULL, %s, %s, %s, %s, %s, %s, 'general')"""           
        args = (
            _data["name"],
            _data["album"],
            _data["artist"],
            _data["duration"],
            _data["description"],
            "C:\\Users\\tong_\\Documents\\Github\\video-sharing-web-backend_1\\src\\asset\\video\\"+_data["name"]+".mp4"
        )

        cursor.execute(sql, args)
        cnx.commit()

        return 'ok', 200

    if request.method == "DELETE":
        id = request.args['id']

        cursor.execute("DELETE FROM videos WHERE id=%s" %id)

        return 'ok', 200

@app.route('/watch', methods=['GET'])
def watch():
    path = request.args['path']

    return send_file(path, as_attachment=True)

@app.route('/search', methods=['GET'])
def search():
    name = request.args['name']
    data = []

    cursor.execute('SELECT * FROM videos WHERE name REGEXP "^%s"' %(name))

    for row in cursor:
        res = {
            'id': row[0],
            'name': row[1],
            'album': row[2],
            'artist': row[3],
            'duration': str(row[4]),
            'description': row[5],
            'path': row[6],
            'privilege': row[7],
        }
        data.append(res)

    return jsonify(data)

@app.route('/users', methods=['GET'])
def users():
    data = get_data_in_format("SELECT * FROM users", '')
    return jsonify(data)

@app.route('/user', methods=['GET', 'POST', 'PUT','DELETE'])
def user():

    if request.method == "GET":
        username = request.args['username']
        data = get_data_in_format("SELECT * FROM users WHERE username=%(username)s", {"username": username})

        return data, 200

    if request.method == "POST":
        _data = request.json
        sql = """INSERT INTO `users`(`id`, `username`, `password`, `firstName`, `lastName`, `token`)
                VALUES (NULL, %s, %s, %s, %s, %s)"""
        args = (
            _data["username"], _data["password"], _data["firstname"], _data["lastname"], sha256.hash(_data["password"]),
        )

        data = get_data_in_format("SELECT * FROM users WHERE username=%(username)s", {"username": _data["username"]})

        if data != '':
            return {'message': 'User {} already exists'.format(data['username'])}

        cursor.execute(sql, args)
        cnx.commit()
        user = get_data_in_format("SELECT * FROM users WHERE username=%(username)s", {"username": _data["username"]})

        return {"username": user["username"], "token": user["token"]}, 201
    
    if request.method == "PUT":
        _data = request.json
        _id = _data["id"]
        for k,v in _data.items():
            if k == "password":
                cursor.execute("UPDATE users SET password= '%s' WHERE id=%s" %(v, _id))
            elif k == "firstName":
                cursor.execute("UPDATE users SET firstName= '%s' WHERE id=%s" %(v, _id))
            elif k == "lastName":
                cursor.execute("UPDATE users SET lastName= '%s' WHERE id=%s" %(v, _id))
        cnx.commit()
        data = get_data_in_format("SELECT * FROM users WHERE id=%(id)s", { "id": _id})

        return data, 201

    if request.method == "DELETE":
        id = request.args['id']

        cursor.execute("DELETE FROM users WHERE id=%s" %id)
        data = get_data_in_format("SELECT * FROM users", '')

        return jsonify(data), 200

@app.route('/user/authenticate', methods=['GET', 'POST'])
def user_auth():

    if request.method == 'POST':
        data = request.json
        user = get_data_in_format("SELECT * FROM users WHERE username=%(username)s", {"username": data["username"]})

        if user:
            if sha256.verify(data["password"], user['token']):
                return {"message": 'Logged in as {}'.format(user["username"]), "token": user["token"]}, 200
            else:
                return {"message": 'Username or password is incorrect'}, 400
        else:
            return {"message": 'Username or password is incorrect'}, 400


if __name__ == '__main__':
	app.run(debug=True)