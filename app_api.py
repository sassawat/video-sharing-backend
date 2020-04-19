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

@app.route('/')
def hello_world():
    return jsonify({"about": 'Hello, World!'})

@app.route('/videos')
def videos():   
    data = []

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
        cursor.close()
        cnx.close()
    return jsonify(data)


@app.route('/video', methods=['GET', 'POST', 'DELETE'])
def video():
    id = request.args['id']
    data = []

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

        if request.method == "GET":
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
                
        elif request.method == "POST":
            data.append("POST")

        elif request.method == "DELETE":
            data.append("DELETE")

        cursor.close()
        cnx.close()
    return jsonify(data)


@app.route('/watch', methods=['GET', 'POST', 'DELETE'])
def watch():
    path = request.args['path']

    return send_file(path, as_attachment=True)


@app.route('/search', methods=['GET'])
def search():
    name = request.args['name']
    data = []

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
        cursor.close()
        cnx.close()

    return jsonify(data)



if __name__ == '__main__':
	app.run(debug=True)