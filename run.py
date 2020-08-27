from flask import Flask, request, send_file, session
import mysql.connector
from mysql.connector import errorcode
import os, datetime, json, time, moviepy.editor
from resources import User, Video
from config import CONFIG_DB, UPLOAD_FOLDER
from flask_cors import CORS, cross_origin

application = Flask(__name__)
CORS(application)
application.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
application.secret_key = "super secret key"
ALLOWED_EXTENSIONS = {'mp4'}

config = CONFIG_DB
cnx = ''

def connect_database():
    global cnx
    # global cursor
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
        # cursor = cnx.cursor()

# Start connect database
connect_database()

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Get duration from vdo
def duration(_file):
	media = moviepy.editor.VideoFileClip(_file)
	minute = media.duration // 60
	sec = media.duration % 60
	if minute < 10:
		return ('0{0:.0f}:{1:.0f}'.format(minute, sec))
	else:
		return ('{0:.0f}:{1:.0f}'.format(minute, sec))

@application.route('/users', methods=['GET'])
def users():
    if not cnx.is_connected():
        connect_database()

    users = User()
    cursor = cnx.cursor()
    return users.getAll(cursor)

@application.route('/user', methods=['GET', 'POST', 'PUT','DELETE'])
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
        return user.register(cnx, data)

    if request.method == "PUT":
        username = request.args['username']
        data = request.json
        return user.update(cnx, username, data)

    if request.method == "DELETE":
        id = request.args['id']
        return user.delete(cnx, id)

@application.route('/user/authenticate', methods=['GET', 'POST', 'PUT'])
def user_auth():
    if not cnx.is_connected():
        connect_database()

    user = User()
    cursor = cnx.cursor()

    if request.method == 'POST':
        data = request.json
        return user.authenticate(cursor, data)

    if request.method == "PUT":
        data = request.json
        return user.setSessionExpire(cnx, data)

@application.route('/watch', methods=['GET'])
def watch():
    if not cnx.is_connected():
        connect_database()

    name = request.args['name']
    full_path = "{}{}.mp4".format(application.config['UPLOAD_FOLDER'], name)

    return send_file(full_path, as_attachment=True)

@application.route('/karaoke', methods=['GET'])
def karaoke():
    if not cnx.is_connected():
        connect_database()

    name = request.args['name']
    full_path = "{}{}_k.mp4".format(application.config['UPLOAD_FOLDER'], name)

    return send_file(full_path, as_attachment=True)

@application.route('/videos')
def videos():
    if not cnx.is_connected():
        connect_database()

    videos = Video()
    cursor = cnx.cursor()
    return videos.getAll(cursor)

@application.route('/video', methods=['GET', 'POST', 'PUT','DELETE'])
def video():
    if not cnx.is_connected():
        connect_database()

    video = Video()
    # cursor = cnx.cursor()

    if request.method == "GET":
        id = request.args['id']
        return video.getVideo(cnx, id)

    if request.method == "POST":
        data = json.loads(request.form.get('data'))

        if 'file' not in request.files:
            print ('No file part')
        file = request.files['file']
        file_k = request.files['file_k']
        # if user does not select file, browser also
        # submit an empty part without filename
        if file.filename == '':
            print ('No selected file')
        filename = file.filename.replace('"', '')
        filename_k = file_k.filename.replace('"', '')
        if file and allowed_file(filename):
            # Save vdo file & add duration
            file.save(os.path.join(application.config['UPLOAD_FOLDER'], "{}.mp4".format(data['name'])))
            data["duration"] = duration("{}{}".format(application.config['UPLOAD_FOLDER'], "{}.mp4".format(data['name'])))
            # Save karaoke file
            file_k.save(os.path.join(application.config['UPLOAD_FOLDER'], "{}_k.mp4".format(data['name'])))

            print ("Upload {} successed".format(filename))

        return video.upload_video(cnx, data)

    if request.method == "DELETE":
        id = request.args['id']
        filename = request.args['name']
        os.remove(os.path.join(application.config['UPLOAD_FOLDER'], "{}.mp4".format(filename)))
        os.remove(os.path.join(application.config['UPLOAD_FOLDER'], "{}_k.mp4".format(filename)))
        print (f"Delete file => {filename} successed!" )

        return video.delete(cnx, id)

@application.route('/search', methods=['GET'])
def search():
    if not cnx.is_connected():
        connect_database()

    video = Video()
    cursor = cnx.cursor()
    name = request.args['name']

    return video.search(cursor, name)

@application.route('/video/top10_like', methods=['GET'])
def top10_like():
    if not cnx.is_connected():
        connect_database()

    videos = Video()
    cursor = cnx.cursor()

    return videos.top10_like(cursor)

@application.route('/video/top10_view', methods=['GET'])
def top10_view():
    if not cnx.is_connected():
        connect_database()

    videos = Video()
    cursor = cnx.cursor()

    return videos.top10_view(cursor)

@application.route('/video/new_of_mounth', methods=['GET'])
def new_of_mounth():
    if not cnx.is_connected():
        connect_database()

    videos = Video()
    cursor = cnx.cursor()

    return videos.new_of_mounth(cursor)

@application.route('/video/addView', methods=['PUT'])
def addView():
    if not cnx.is_connected():
        connect_database()

    video = Video()

    if request.method == 'PUT':
        id = request.args['id']

        return video.addView(cnx, id)

@application.route('/video/addLike', methods=['PUT'])
def addLike():
    if not cnx.is_connected():
        connect_database()

    video = Video()
    
    if request.method == 'PUT':
        id = request.args['id']

        return video.addLike(cnx, id)

@application.route('/video/addDownload', methods=['PUT'])
def addDownload():
    if not cnx.is_connected():
        connect_database()

    video = Video()
    
    if request.method == 'PUT':
        id = request.args['id']

        return video.addDownload(cnx, id)


if __name__ == '__main__':
	application.run(debug=true, host='0.0.0.0')
