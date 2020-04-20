from flask import Flask, jsonify, request, send_file
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
        query = """INSERT INTO `videos`(`id`, `name`, `album`, `artist`, `duration`, `description`, `path`, `privilege`)
                VALUES (NULL, %s, %s, %s, %s, %s, %s, 'general')"""           
        args = (
            _data["name"],
            _data["album"],
            _data["artist"],
            _data["duration"],
            _data["description"],
            "C:\\Users\\tong_\\Documents\\Github\\video-sharing-web-backend_1\\src\\asset\\video\\"+_data["name"]+".mp4"
        )

        cursor.execute(query, args)
        cnx.commit()

        return 'ok', 200

    if request.method == "DELETE":
        data.append("DELETE")



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
    data = []

    cursor.execute("SELECT * FROM users")

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

    return jsonify(data)


@app.route('/user', methods=['GET', 'POST', 'PUT','DELETE'])
def user():
    data = []

    if request.method == "GET":
        username = request.args['username']

        cursor.execute("SELECT * FROM users WHERE username='%s'" %(username))
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

        return jsonify(data)

    if request.method == "POST":
        _data = request.json
        query = """INSERT INTO `users`(`id`, `username`, `password`, `firstName`, `lastName`, `token`)
                VALUES (NULL, %s, %s, %s, %s, %s)"""
        args = (
            _data["username"],
            _data["password"],
            _data["firstName"],
            _data["lastName"],
            _data["token"],
        )
        cursor.execute(query, args)
        cnx.commit()

        return 'ok', 200


@app.route('/user/authenticate', methods=['GET', 'POST'])
def user_auth():

    if request.method == 'POST':
        data = request.json
        cursor.execute("SELECT username, password FROM users WHERE username='%s'" %(data["username"]))

        for row in cursor:
            res = {
                'username': row[0],
                'password': row[1],
            }

        if res:
            if data["password"] == res['password']:
                return ('ok'), 200
            else:
                return ('Username or password is incorrect'), 404
        else:
            return ('Username or password is incorrect'), 404


if __name__ == '__main__':
	app.run(debug=True)