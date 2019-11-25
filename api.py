from flask import request,Flask,json,jsonify, Response
import MySQLdb
import MySQLdb.cursors as cursors
import json
app = Flask(__name__)

global db, cursor

# disconnect from server
#db.close()
def connect_db():
    global db, cursor
    # Open database connection
    db = MySQLdb.connect("localhost", "root", "sukanya27", "insurance", cursorclass=cursors.DictCursor)

    # prepare a cursor object using cursor() method
    cursor = db.cursor()

@app.route('/users')
def users():
    data = get_user_details()
    return jsonify(data
                   )
@app.route('/users/<id>')
def get_user(id):
    data = get_user_details(id=id)
    if not data:
        return Response('{"error":"user doesn\'t exit"}', status=404, mimetype='application/json')
    return jsonify(data
                   )
@app.route('/users',methods=["POST"])
def create_user():
    body = request.get_json()
    if "name" not in body or "email" not in body or "ph_no" not in body:
        return Response('{"error":"name, email and ph_no are required"}', status=400, mimetype='application/json')
    name = body["name"]
    email = body["email"]
    ph_no = body["ph_no"]

    data = get_user_details(email=email)
    if data:
        return Response('{"error":"email is already registered"}', status=400, mimetype='application/json')
    sql = "insert into users (name,email,ph_no) values ('%s','%s','%s')" %(name,email,ph_no)
    try:
        # Execute the SQL command
        cursor.execute(sql)
        # Commit your changes in the database
        db.commit()
    except:
        # Rollback in case there is any error
        db.rollback()

    data = get_user_details(email=email)
    return Response(json.dumps(data) , status=201, mimetype='application/json')

@app.route('/users/<id>',methods=["PUT"])
def update_user(id):
    data = get_user_details(id=id)
    if not data:
        return Response('{"error":"user not exist"}', status=404, mimetype='application/json')
    body = request.get_json()
    if "name" not in body and "email" not in body and "ph_no" not in body:
        return Response('{"error":"name, email and ph_no are required"}', status=400, mimetype='application/json')
    sql = "update users set "
    if "name" in body:
        sql += "name = '%s',"% body["name"]
    if "email" in body:
        sql += "email = '%s',"% body["email"]
    if "ph_no" in body:
        sql += "ph_no = '%s',"% body["ph_no"]
    sql = sql[:-1]
    sql += " where id = %s"%id
    #print sql

    try:
        # Execute the SQL command
        cursor.execute(sql)
        # Commit your changes in the database
        db.commit()
    except Exception,e:
        # Rollback in case there is any error
        db.rollback()
        print str(e)

    data = get_user_details(id=id)
    return Response(json.dumps(data) , status=200, mimetype='application/json')

@app.route('/users/<id>',methods=["DELETE"])
def delete_user(id):
    data = get_user_details(id=id)
    if not data:
        return Response('{"error":"user not exist"}', status=404, mimetype='application/json')

    sql = "delete from users where id = %s"%id
    #print sql

    try:
        # Execute the SQL command
        cursor.execute(sql)
        # Commit your changes in the database
        db.commit()
    except Exception,e:
        # Rollback in case there is any error
        db.rollback()
        print str(e)

    data = get_user_details(id=id)
    if data:
        return Response('{"error":"user not deleted"}', status=500, mimetype='application/json')
    return Response(status=204, mimetype='application/json')

def get_user_details(id=None,email=None):
    connect_db()
    if id:
        sql = "select * from users where id=%s"%id
    elif email:
        sql = "select * from users where email='%s'" %email
    else:
        sql = "select * from users"
    cursor.execute(sql)
    data = cursor.fetchall()
    return data
if __name__ == '__main__':
    app.run(debug=True)