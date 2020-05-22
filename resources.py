from flask import jsonify
from passlib.hash import pbkdf2_sha256 as sha256
import datetime, random, string
from config import UPLOAD_FOLDER

def get_db_all_user(cursor):
    data = []
    # cursor = cnx.cursor()
    cursor.execute("SELECT * FROM users ORDER BY id DESC")
    for row in cursor:
        res = {
            'id': row[0],
            'username': row[1],
            'password': row[2],
            'Fname': row[3],
            'Lname': row[4],
            'phone': row[5],
            'token': row[6],
            'privilege': row[7],
            'num_of_sing': row[8],
            'time_to_service': row[9]
        }
        data.append(res)

    cursor.close()

    return data

def get_db_user(cursor, username):
    # cursor = cnx.cursor()
    cursor.execute("SELECT * FROM users WHERE username=%(username)s", {"username": username})
    res = ''

    for row in cursor:
        res = {
            'id': row[0],
            'username': row[1],
            'password': row[2],
            'Fname': row[3],
            'Lname': row[4],
            'phone': row[5],
            'token': row[6],
            'privilege': row[7],
            'num_of_sing': row[8],
            'time_to_service': row[9]
        }

    cursor.close()

    return res

def compareUserData(newData, currentData):
    lis = [item[1] for item in sorted(newData.items())]
    lis_2 = [item2[1] for item2 in sorted(currentData.items())]
    full_lis = sorted(newData.items())
    dic = {}
    for j in range(0, len(lis)):
        if lis[j] != lis_2[j]:
            dic[full_lis[j][0]] = full_lis[j][1]

    return dic

def get_random_alphaNumeric_string(stringLength=8):
    lettersAndDigits = string.ascii_letters + string.digits
    return ''.join((random.choice(lettersAndDigits) for i in range(stringLength)))

class User():

    def getAll(self, cursor):
        return jsonify(get_db_all_user(cursor)), 200

    def getUser(self, cursor, username):
        return get_db_user(cursor, username), 200

    def register(self, cnx, data):
        if data["username"] == '':
            username = get_random_alphaNumeric_string()
            password = get_random_alphaNumeric_string()
            print ("{} and {}".format(username, password))
        else:
            username = data["username"]
            password = data["password"]

        user_existing = get_db_user(cnx.cursor(), username)
        if user_existing:
            return {'message': 'User {} already exists'.format(username)}
        # Set params
        sql = """INSERT INTO `users`(`id`, `username`, `password`, `Fname`, `Lname`, `phone`, `token`, `privilege`, `num_of_sing`, `time_to_service`)
                VALUES (NULL, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
        args = (
            username, password, data["Fname"], data["Lname"], data["phone"], sha256.hash(password), 'user', 5, 60
        )
        # Execute
        cursor = cnx.cursor()
        cursor.execute(sql, args)
        cnx.commit()
        user = get_db_user(cursor, username)

        return {"username": user["username"], "token": user["token"]}, 201

    def update(self, cnx, username, data):
        data = compareUserData(data, get_db_user(cnx.cursor(), username))
        cursor = cnx.cursor()

        for k,v in data.items():
            if k == "password":
                cursor.execute("UPDATE users SET password= '%s', token='%s' WHERE username='%s'" %(v, sha256.hash(v), username))
            elif k == "Fname":
                cursor.execute("UPDATE users SET Fname= '%s' WHERE username='%s'" %(v, username))
            elif k == "Lname":
                cursor.execute("UPDATE users SET Lname= '%s' WHERE username='%s'" %(v, username))
            elif k == "phone":
                cursor.execute("UPDATE users SET phone= '%s' WHERE username='%s'" %(v, username))
            elif k == "privilege":
                cursor.execute("UPDATE users SET privilege= '%s' WHERE username='%s'" %(v, username))
            elif k == "num_of_sing":
                cursor.execute("UPDATE users SET num_of_sing= '%s' WHERE username='%s'" %(v, username))
            elif k == "time_to_service":
                cursor.execute("UPDATE users SET time_to_service= '%s' WHERE username='%s'" %(v, username))

        cnx.commit()

        return jsonify(get_db_all_user(cursor)), 201
    
    def delete(self, cnx, id):
        cursor = cnx.cursor()
        cursor.execute("DELETE FROM users WHERE id=%s" %id)
        cnx.commit()
        
        return jsonify(get_db_all_user(cursor)), 200

    def authenticate(self, cursor, data):
        user = get_db_user(cursor, data["username"])

        if user:
            if sha256.verify(data["password"], user['token']):
                res = {
                    "id": user["id"],
                    "token": user["token"],
                    "privilege": user["privilege"],
                    "num_of_sing": user["num_of_sing"],
                    "time_to_service": user["time_to_service"]
                }
                return res, 200
            else:
                return {"message": 'Password is incorrect'}, 400
        else:
            return {"message": 'Username is incorrect'}, 400

    def setSessionExpire(self, cnx, data):
        _id = data["id"]
        cursor = cnx.cursor()
        cursor.execute("UPDATE users SET num_of_sing= '%s', time_to_service= '%s' WHERE id='%s'" %(0, 0, _id))
        cnx.commit()

        return {"message": 'ok'}, 200

class Video():
    def getAll(self, cursor):
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
                'privilege': row[6],
                'like_rate':row[7],
                'view_rate':row[8],
                'download_rate':row[9]
            }
            data.append(res)

        cursor.close()

        return jsonify(data)

    def getVideo(self, cnx, id):
        data = []
        cursor = cnx.cursor()
        cursor.execute("SELECT * FROM videos WHERE id={}".format(id))

        for row in cursor:
            res = {
                'id': row[0],
                'name': row[1],
                'album': row[2],
                'artist': row[3],
                'duration': str(row[4]),
                'description': row[5],
                'privilege': row[6],
            }
            data.append(res)

        cursor.close()

        return jsonify(data)

    def upload_video(self, cnx, data):
        sql = """INSERT INTO `videos`(`id`, `name`, `album`, `artist`, `duration`, `description`, `privilege`, `like_rate`, `view_rate`, `download_rate`, `time_upload`)
                VALUES (NULL, %s, %s, %s, %s, %s, 'general', 0, 0, 0, %s)"""           
        args = (
            data["name"],
            data["album"],
            data["artist"],
            data["duration"],
            data["description"],
            datetime.datetime.now()
        )
        # Execute
        cursor = cnx.cursor()
        cursor.execute(sql, args)
        cnx.commit()
        cursor.close()

        return {"message": 'Add video successed'}, 201

    def delete(self, cnx, id):
        cursor = cnx.cursor()
        cursor.execute("DELETE FROM videos WHERE id=%s" %id)
        cnx.commit()
        cursor.close()

        return {"message": 'Delete video successed'}, 200

    def search(self, cursor, name):
        data = []
        cursor.execute('SELECT * FROM videos where CONCAT(name, artist) REGEXP "^%s"' %(name))

        for row in cursor:
            res = {
                'id': row[0],
                'name': row[1],
                'album': row[2],
                'artist': row[3],
                'duration': str(row[4]),
                'description': row[5],
                'privilege': row[6],
            }
            data.append(res)

        cursor.close()

        return jsonify(data)

    def top10_like(self, cursor):
        data = []
        cursor.execute("SELECT * FROM `videos` ORDER BY `videos`.`like_rate` DESC LIMIT 10")

        for row in cursor:
            res = {
                'id': row[0],
                'name': row[1],
                'album': row[2],
                'artist': row[3],
                'duration': str(row[4]),
                'description': row[5],
                'privilege': row[6],
                'like_rate':row[7],
                'view_rate':row[8]
            }
            data.append(res)

        return jsonify(data)

    def top10_view(self, cursor):
        data = []
        cursor.execute("SELECT * FROM `videos` ORDER BY `videos`.`view_rate` DESC LIMIT 10")

        for row in cursor:
            res = {
                'id': row[0],
                'name': row[1],
                'album': row[2],
                'artist': row[3],
                'duration': str(row[4]),
                'description': row[5],
                'privilege': row[6],
                'like_rate':row[7],
                'view_rate':row[8]
            }
            data.append(res)

        cursor.close()

        return jsonify(data)

    def new_of_mounth(self, cursor):
        data = []
        
        x = datetime.datetime.now()
        sql = "SELECT * FROM `videos` WHERE `time_upload` BETWEEN %s AND %s ORDER BY `time_upload` DESC"
        args = ('%s-%s-01'%(x.year, x.strftime("%m")), '%s-%s-31'%(x.year, x.strftime("%m")))
        cursor.execute(sql, args)

        for row in cursor:
            res = {
                'id': row[0],
                'name': row[1],
                'album': row[2],
                'artist': row[3],
                'duration': str(row[4]),
                'description': row[5],
                'privilege': row[6],
                'like_rate':row[7],
                'view_rate':row[8],
                'upload_time':row[9]
            }
            data.append(res)

        return jsonify(data)

    def addView(self, cnx, id):
        cursor = cnx.cursor()
        cursor.execute("SELECT `view_rate` FROM `videos` WHERE id = %s" %(id))
        add_view = cursor.fetchone()[0]+1
        cursor.execute("UPDATE `videos` SET `view_rate`= %s WHERE `id` = %s" %(add_view, id))
        cnx.commit()
        cursor.close()

        return {"message": 'ok'}, 201

    def addLike(self, cnx, id):
        cursor = cnx.cursor()
        cursor.execute("SELECT `like_rate` FROM `videos` WHERE id = %s" %(id))
        add_like = cursor.fetchone()[0]+1
        cursor.execute("UPDATE `videos` SET `like_rate`= %s WHERE `id` = %s" %(add_like, id))
        cnx.commit()
        cursor.close()

        return {"message": 'ok'}, 201

    def addDownload(self, cnx, id):
        cursor = cnx.cursor()
        cursor.execute("SELECT `download_rate` FROM `videos` WHERE id = %s" %(id))
        add_download = cursor.fetchone()[0]+1
        cursor.execute("UPDATE `videos` SET `download_rate`= %s WHERE `id` = %s" %(add_download, id))
        cnx.commit()
        cursor.close()

        return {"message": 'ok'}, 201