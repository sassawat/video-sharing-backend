import mysql.connector
# from mysql.connector import errorcode

try:
    cnx = mysql.connector.connect(
        user="root", 
        password="123456", 
        host="10.0.253.241", 
        port=9988, 
        database="video_sharing"
        )
except mysql.connector.Error as err:
  if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
    print("Something is wrong with your user name or password")
  elif err.errno == errorcode.ER_BAD_DB_ERROR:
    print("Database does not exist")
  else:
    print(err)
else:
    print ("Connect database successed.")
    print (cnx)
    cursor = cnx.cursor()
    print (cursor)
    query = ("SELECT * FROM videos WHERE id=%s" %(1))
    int_data = ('1')
    cursor.execute(query)
    for row in cursor:
        print(row)
    # print (cursor)
    cursor.close()
    cnx.close()

