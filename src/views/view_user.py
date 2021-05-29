from flask import Blueprint, jsonify, request
import psycopg2
import sys
sys.path.append('..')
from auth.auth_jwt import auth_token, encode_token
from database.database import db_connection


user = Blueprint('user', __name__, url_prefix='/dbproj/user')


@user.route('', methods=['POST'])
def create_user():
    payload = request.get_json()

    connection = db_connection()
    cursor = connection.cursor()

    statement = """insert into users(email, password, username) values(%s, %s, %s) returning user_id"""

    values = (payload['email'], payload['password'], payload['username'])

    try:
        cursor.execute(statement, values)
        rows = cursor.fetchall()

        cursor.execute('commit')

        result = {"user_id":  int(rows[0][0])}
    except (Exception, psycopg2.DatabaseError) as error:
        result = {"error": str(error)}
    finally:
        if connection is not None:
            connection.close()

    return jsonify(result)


@user.route('', methods=['PUT'])
def authentication_user():
    content = request.get_json()

    connection = db_connection()
    cursor = connection.cursor()

    statement = """select user_id from users where username = %s and password = %s """

    values = (content['username'], content['password'])

    try:
        cursor.execute(statement, values)
        if cursor.rowcount==0:
            result = {"error": 'Not found'}
        else:
            rows = cursor.fetchall()
            user_id = int(rows[0][0])

            token = encode_token(user_id)
            
            result = {"auth_token": token}

    except (Exception, psycopg2.DatabaseError) as error:
        result = {"error": str(error)}
    finally:
        if connection is not None:
            connection.close()
    return jsonify(result)

