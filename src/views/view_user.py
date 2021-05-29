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

    required_values = ['email', 'password', 'username']
    for value in required_values:
        if value not in payload:
            return jsonify({'error': 'Invalid payload arguments'})

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
    payload = request.get_json()

    required_values = ['username', 'password']
    for value in required_values:
        if value not in payload:
            return jsonify({'error': 'Invalid payload arguments'})

    connection = db_connection()
    cursor = connection.cursor()

    statement = """select user_id from users where username = %s and password = %s """

    values = (payload['username'], payload['password'])

    try:
        cursor.execute(statement, values)
        rows = cursor.fetchall()
        if len(rows) == 0:
            result = {"error": 'Not found'}
        else:
            user_id = int(rows[0][0])

            token = encode_token(user_id)
            
            result = {"auth_token": token}

    except (Exception, psycopg2.DatabaseError) as error:
        result = {"error": str(error)}
    finally:
        if connection is not None:
            connection.close()
    return jsonify(result)

