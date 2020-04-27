from flask import Flask, request, send_file, session
import mysql.connector
import os, datetime, json
from resources import User, Video

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'C:\\Users\\tong_\\Documents\\Github\\video-sharing-web-backend_1\\src\\asset\\video'
app.secret_key = "super secret key"
ALLOWED_EXTENSIONS = {'mp4'}

config = {
    "user": "root", 
    "password": "123456", 
    "host": "10.0.253.241", 
    "port": 9988, 
    "database": "video_sharing"
    }

cnx = ''

def connect_database():
    global cnx
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

# Start connect database
connect_database()

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/users', methods=['GET'])
def users():
    if not cnx.is_connected():
        connect_database()

    users = User()
    cursor = cnx.cursor()
    return users.getAll(cursor)

@app.route('/user', methods=['GET', 'POST', 'PUT','DELETE'])
def user():
    if not cnx.is_connected():
        connect_database()

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
    if not cnx.is_connected():
        connect_database()

    user = User()
    cursor = cnx.cursor()

    if request.method == 'POST':
        data = request.json
        return user.authenticate(cursor, data)

@app.route('/watch', methods=['GET'])
def watch():
    if not cnx.is_connected():
        connect_database()

    path = request.args['path']

    return send_file(path, as_attachment=True)

@app.route('/videos')
def videos():
    if not cnx.is_connected():
        connect_database()

    videos = Video()
    cursor = cnx.cursor()
    return videos.getAll(cursor)

@app.route('/video', methods=['GET', 'POST', 'PUT','DELETE'])
def video():
    if not cnx.is_connected():
        connect_database()

    video = Video()
    cursor = cnx.cursor()

    if request.method == "GET":
        id = request.args['id']
        return video.getVideo(cursor, id)

    if request.method == "POST":
        data = json.loads(request.form.get('data'))
        
        if 'file' not in request.files:
            print ('No file part')
        file = request.files['file']
        # if user does not select file, browser also
        # submit an empty part without filename
        if file.filename == '':
            print ('No selected file')
        filename = file.filename.replace('"', '')
        if file and allowed_file(filename):
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], "{}.mp4".format(data['name'])))
            print ("Upload {} successed".format(filename))
                                    
        return video.upload_video(cnx, data)

    if request.method == "DELETE":
        id = request.args['id']
        return video.delete(cursor, id)

@app.route('/search', methods=['GET'])
def search():
    if not cnx.is_connected():
        connect_database()

    video = Video()
    cursor = cnx.cursor()
    name = request.args['name']
    return video.search(cursor, name)


if __name__ == '__main__':
	app.run(debug=True)