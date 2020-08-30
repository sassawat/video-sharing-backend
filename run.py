from flask import Flask, request, send_file, session, redirect
from mysql.connector import errorcode
from resources import User, Video
from config import CONFIG_DB, UPLOAD_FOLDER, BACKEND_ADDR, WEB_ADDR
from flask_cors import CORS, cross_origin
import os, datetime, json, time, moviepy.editor
import mysql.connector, requests, getmac

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

@application.route('/user/auth/gmail', methods=['POST'])
def auth_gmail():
    if not cnx.is_connected():
        connect_database()

    user = User()
    cursor = cnx.cursor()

    if request.method == 'POST':
        data = request.json
        return user.auth_social(cnx, cursor, data)

@application.route('/user/auth/line', methods=['GET'])
def auth_line():
    if not cnx.is_connected():
        connect_database()

    user = User()
    cursor = cnx.cursor()
    
    if request.method == "GET":
        id = request.args['id']
        data = {'id': id}
        return user.auth_social(cnx, cursor, data)

@application.route('/user/auth/mac', methods=['GET', 'POST'])
def auth_mac():
    if not cnx.is_connected():
        connect_database()

    user = User()
    cursor = cnx.cursor()
    
    if request.method == "GET":
        mac = getmac.get_mac_address()
        # res = user.auth_mac_addr(cursor, mac)
        # cnx.close()
        if mac:
            return mac, 200
        else:
            return {"msg": "not ok"}, 401
    
    if request.method == "POST":
        data = request.json
        res = user.auth_mac_addr(cursor, data["mac"])
        cnx.close()
        if res:
            return res, 200
        else:
            return {"msg": "not ok"}, 401
    
@application.route('/user/auth/line/callback', methods=['POST', 'GET'])
def auth_line_callback():
    if not cnx.is_connected():
        connect_database()

    user = User()
    cursor = cnx.cursor()

    if request.method == 'GET':
        code = request.args['code']
        state = request.args['state']

        get_token_url = "https://api.line.me/v2/oauth/accessToken"
        get_profile_url = "https://api.line.me/v2/profile"

        payload = {
            'grant_type': 'authorization_code',
            'client_id': '1654879183',
            'client_secret': 'ef7a32d804fe144f54d4cad9ceb3825b',
            'code': code,
            'redirect_uri': '{}/user/auth/line/callback'.format(BACKEND_ADDR)
        }

        get_token_headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        get_token_response = requests.request("POST", get_token_url, headers=get_token_headers, data=payload)
        access_token = json.loads(get_token_response.content)["access_token"]
 
        get_profile_headers = {'Authorization': 'Bearer {}'.format(access_token)}
        get_profile_response = requests.request("GET", get_profile_url, headers=get_profile_headers)
        profile = json.loads(get_profile_response.content)
        
        data = {
            "id": profile["userId"],
            "email": 'P@ssw0rd',
            "firstName": '',
            "lastName": '',
            "authToken": access_token
        }
        user.auth_social(cnx, cursor, data)
        # return {"token": json.loads(get_token_response.content), "profile": profile}, 200
        return redirect('{}/#/login?id={}'.format(WEB_ADDR, profile["userId"]))

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

@application.route('/checkOTP', methods=['POST'])
def checkOTP():   
    if request.method == "POST":
        data = request.json
        # print (data)
        url = "http://203.114.102.213/r18sendu.php"

        payload = {
            'usn': '021507940',
            'psw': '9312tpwy',
            'org': '021507940',
            'destination': data["destination"],
            'msg': 'OTP = {} [รหัสอ้างอิงในการลงทะเบียนระบบ Karaoke On Demand]'.format(data["otp"])
        }

        response = requests.request("POST", url, data = payload)
        return {"message": response.text}, 200


if __name__ == '__main__':
	application.run(debug=True, host='0.0.0.0')
