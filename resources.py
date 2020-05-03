from flask import jsonify
from passlib.hash import pbkdf2_sha256 as sha256
import datetime

def get_db_all_user(cursor):
    data = []
    # cursor = cnx.cursor()
    cursor.execute("SELECT * FROM users")
    for row in cursor:
        res = {
            'id': row[0],
            'username': row[1],
            'password': row[2],
            'firstName': row[3],
            'lastName': row[4],
            'token': row[5],
            'privilege': row[6]
        }
        data.append(res)

    cursor.close()

    return data

def get_db_user(cursor, username):
    # cursor = cnx.cursor()
    cursor.execute("SELECT * FROM users WHERE username=%(username)s", {"username": username})

    for row in cursor:
        res = {
            'id': row[0],
            'username': row[1],
            'password': row[2],
            'firstName': row[3],
            'lastName': row[4],
            'token': row[5],
            'privilege': row[6]
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

class User():

    def getAll(self, cursor):
        return jsonify(get_db_all_user(cursor)), 200

    def getUser(self, cursor, username):
        return get_db_user(cursor, username), 200

    def register(self, cnx, cursor, data):
        user_existing = get_user(cursor, data["username"])
        if user_existing:
            return {'message': 'User {} already exists'.format(data['username'])}

        sql = """INSERT INTO `users`(`id`, `username`, `password`, `firstName`, `lastName`, `token`, `privilege`)
                VALUES (NULL, %s, %s, %s, %s, %s, %s)"""
        args = (
            data["username"], data["password"], data["firstname"], data["lastname"], sha256.hash(data["password"]), 'user'
        )

        cursor.execute(sql, args)
        user = get_db_user(cursor, data["username"])

        return {"username": user["username"], "token": user["token"]}, 201

    def update(self, cnx, username, data):
        data = compareUserData(data, get_db_user(cnx.cursor(), username))
        cursor = cnx.cursor()

        for k,v in data.items():
            if k == "password":
                cursor.execute("UPDATE users SET password= '%s', token='%s' WHERE username='%s'" %(v, sha256.hash(v), username))
            elif k == "firstName":
                cursor.execute("UPDATE users SET firstName= '%s' WHERE username='%s'" %(v, username))
            elif k == "lastName":
                cursor.execute("UPDATE users SET lastName= '%s' WHERE username='%s'" %(v, username))
            elif k == "privilege":
                cursor.execute("UPDATE users SET privilege= '%s' WHERE username='%s'" %(v, username))

        cnx.commit()
        print (get_db_user(cursor, username))

        return {"message": 'Change user data successed'}, 201
    
    def delete(self, cnx, id):
        cursor = cnx.cursor()
        cursor.execute("DELETE FROM users WHERE id=%s" %id)
        cnx.commit()
        
        return jsonify(get_db_all_user(cursor)), 200

    def authenticate(self, cursor, data):
        user = get_db_user(cursor, data["username"])

        if user:
            if sha256.verify(data["password"], user['token']):
                return {"id": user["id"], "token": user["token"], "privilege": user["privilege"]}, 200
            else:
                return {"message": 'Password is incorrect'}, 400
        else:
            return {"message": 'Username is incorrect'}, 400

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
                'path': row[6],
                'privilege': row[7],
                'favorite_rate':row[8],
                'view_rate':row[9]
            }
            data.append(res)
        cursor.close()

        return jsonify(data)

    def getVideo(self, cursor, id):
        data = []
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
        cursor.close()

        return jsonify(data)

    def upload_video(self, cnx, data):
        sql = """INSERT INTO `videos`(`id`, `name`, `album`, `artist`, `duration`, `description`, `path`, `privilege`, `favorite_rate`, `view_rate`, `time_upload`)
                VALUES (NULL, %s, %s, %s, %s, %s, %s, 'general', 0, 0, %s)"""           
        args = (
            data["name"],
            data["album"],
            data["artist"],
            '-',
            data["description"],
            "C:\\Users\\tong_\\Documents\\Github\\video-sharing-web-backend_1\\src\\asset\\video\\"+data["name"]+".mp4",
            datetime.datetime.now()
        )

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
        # print (data)
        cursor.close()

        return jsonify(data)

    def top10_favorite(self, cursor):
        data = []
        cursor.execute("SELECT * FROM `videos` ORDER BY `videos`.`favorite_rate` DESC LIMIT 10")

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
                'favorite_rate':row[8],
                'view_rate':row[9]
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
                'path': row[6],
                'privilege': row[7],
                'favorite_rate':row[8],
                'view_rate':row[9]
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
                'path': row[6],
                'privilege': row[7],
                'favorite_rate':row[8],
                'view_rate':row[9],
                'upload_time':row[10]
            }
            data.append(res)

        return jsonify(data)