from flask import Flask, request, send_file, session
import mysql.connector
import os, datetime, json, time, vlc
from resources import User, Video
from config import CONFIG_DB, UPLOAD_FOLDER
from flask_cors import CORS, cross_origin

app = Flask(__name__)
CORS(app)
# cors = CORS(app, resources={r"/": {"origins": "*"}})
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.secret_key = "super secret key"
ALLOWED_EXTENSIONS = {'mp4'}

config = CONFIG_DB
cnx = ''
# cursor = ''

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

# ต้องติดตั้งแอพ VLC ด้วย ถึงจะ import vlc
def duration(_file):
	vlc_instance = vlc.Instance()
	player = vlc_instance.media_player_new()
	media = vlc_instance.media_new(_file)
	player.set_media(media)
	player.play()
	time.sleep(1)
	duration = player.get_length() / 1000
	player.stop()
	minute = duration // 60
	sec = duration % 60
	if minute < 10:
		return ('0{0:.0f}:{1:.0f}'.format(minute, sec))
	else:
		return ('{0:.0f}:{1:.0f}'.format(minute, sec))

@app.route('/users', methods=['GET'])
# @cross_origin(origin='*',headers=['Content-Type','Authorization'])
def users():
    if not cnx.is_connected():
        connect_database()

    users = User()
    cursor = cnx.cursor()
    return users.getAll(cursor)

@app.route('/user', methods=['GET', 'POST', 'PUT','DELETE'])
# @cross_origin(origin='*',headers=['Content-Type','Authorization'])
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

@app.route('/user/authenticate', methods=['GET', 'POST', 'PUT'])
# @cross_origin(origin='*',headers=['Content-Type','Authorization'])
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

@app.route('/watch', methods=['GET'])
# @cross_origin(origin='*',headers=['Content-Type','Authorization'])
def watch():
    if not cnx.is_connected():
        connect_database()

    name = request.args['name']
    full_path = "{}\\{}.mp4".format(app.config['UPLOAD_FOLDER'], name)

    return send_file(full_path, as_attachment=True)

@app.route('/karaoke', methods=['GET'])
# @cross_origin(origin='*',headers=['Content-Type','Authorization'])
def karaoke():
    if not cnx.is_connected():
        connect_database()

    name = request.args['name']
    full_path = "{}\\{}_k.mp4".format(app.config['UPLOAD_FOLDER'], name)

    return send_file(full_path, as_attachment=True)

@app.route('/videos')
# @cross_origin(origin='*',headers=['Content-Type','Authorization'])
def videos():
    if not cnx.is_connected():
        connect_database()

    videos = Video()
    cursor = cnx.cursor()
    return videos.getAll(cursor)

@app.route('/video', methods=['GET', 'POST', 'PUT','DELETE'])
# @cross_origin(origin='*',headers=['Content-Type','Authorization'])
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
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], "{}.mp4".format(data['name'])))
            data["duration"] = duration("{}\\{}".format(app.config['UPLOAD_FOLDER'], "{}.mp4".format(data['name'])))

            # Save karaoke file
            file_k.save(os.path.join(app.config['UPLOAD_FOLDER'], "{}_k.mp4".format(data['name'])))

            # print (data)
            print ("Upload {} successed".format(filename))

        # time.sleep(10000)               
        return video.upload_video(cnx, data)

    if request.method == "DELETE":
        id = request.args['id']
        filename = request.args['name']
        os.remove(os.path.join(app.config['UPLOAD_FOLDER'], "{}.mp4".format(filename)))
        os.remove(os.path.join(app.config['UPLOAD_FOLDER'], "{}_k.mp4".format(filename)))
        print ("Delete file => " + filename)
        return video.delete(cnx, id)

@app.route('/search', methods=['GET'])
# @cross_origin(origin='*',headers=['Content-Type','Authorization'])
def search():
    if not cnx.is_connected():
        connect_database()

    video = Video()
    cursor = cnx.cursor()
    name = request.args['name']
    return video.search(cursor, name)

@app.route('/video/top10_like', methods=['GET'])
# @cross_origin(origin='*',headers=['Content-Type','Authorization'])
def top10_like():
    if not cnx.is_connected():
        connect_database()

    videos = Video()
    cursor = cnx.cursor()
    return videos.top10_like(cursor)

@app.route('/video/top10_view', methods=['GET'])
# @cross_origin(origin='*',headers=['Content-Type','Authorization'])
def top10_view():
    if not cnx.is_connected():
        connect_database()

    videos = Video()
    cursor = cnx.cursor()
    return videos.top10_view(cursor)

@app.route('/video/new_of_mounth', methods=['GET'])
# @cross_origin(origin='*',headers=['Content-Type','Authorization'])
def new_of_mounth():
    if not cnx.is_connected():
        connect_database()

    videos = Video()
    cursor = cnx.cursor()
    return videos.new_of_mounth(cursor)

@app.route('/video/addView', methods=['PUT'])
# @cross_origin(origin='*',headers=['Content-Type','Authorization'])
def addView():
    if not cnx.is_connected():
        connect_database()

    video = Video()

    if request.method == 'PUT':
        id = request.args['id']
        return video.addView(cnx, id)

@app.route('/video/addLike', methods=['PUT'])
# @cross_origin(origin='*',headers=['Content-Type','Authorization'])
def addLike():
    if not cnx.is_connected():
        connect_database()

    video = Video()
    
    if request.method == 'PUT':
        id = request.args['id']
        return video.addLike(cnx, id)


if __name__ == '__main__':
	app.run()