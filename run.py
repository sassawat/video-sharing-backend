from flask import Flask, request, send_file
import mysql.connector
import datetime
from resources import User, Video

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


@app.route('/users', methods=['GET'])
def users():
    users = User()
    cursor = cnx.cursor()
    return users.getAll(cursor)

@app.route('/user', methods=['GET', 'POST', 'PUT','DELETE'])
def user():
    user = User()
    cursor = cnx.cursor()

    if request.method == "GET":
        username = request.args['username']
        return user.getUser(cursor, username)
    
    if request.method == "POST":
        data = request.json
        return user.register(cnx, cursor, data)

    if request.method == "PUT":
        username = request.args['username']
        data = request.json
        return user.update(cnx, username, data)

    if request.method == "DELETE":
        id = request.args['id']
        return user.delete(cursor, id)

@app.route('/user/authenticate', methods=['GET', 'POST'])
def user_auth():
    user = User()
    cursor = cnx.cursor()

    if request.method == 'POST':
        data = request.json
        return user.authenticate(cursor, data)

@app.route('/watch', methods=['GET'])
def watch():
    path = request.args['path']

    return send_file(path, as_attachment=True)

@app.route('/videos')
def videos():
    videos = Video()
    cursor = cnx.cursor()
    return videos.getAll(cursor)

@app.route('/video', methods=['GET', 'POST', 'PUT','DELETE'])
def video():
    video = Video()
    cursor = cnx.cursor()

    if request.method == "GET":
        id = request.args['id']
        return video.getVideo(cursor, id)

    if request.method == "POST":
        data = request.json
        return video.addVideo(cnx, data)

    if request.method == "DELETE":
        id = request.args['id']
        return video.delete(cursor, id)

@app.route('/search', methods=['GET'])
def search():
    video = Video()
    cursor = cnx.cursor()
    name = request.args['name']
    return video.search(cursor, name)


if __name__ == '__main__':
	app.run(debug=True)