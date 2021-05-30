import psycopg2
from flask import Blueprint, jsonify, request
from auth.auth_jwt import encode_token
from database.database import db_connection


user = Blueprint('user', __name__, url_prefix='/dbproj/user')


@user.route('', methods=['POST'])
def create_user():
    """
    ROUTE (POST): /dbproj/user

    Creates new user with the given information

    :return: User id or an error if something went wrong
    """

    # Payload with the user information
    payload = request.get_json()

    connection = db_connection()
    cursor = connection.cursor()

    required_values = ['email', 'password', 'username']

    # Check if the payload contains all of the needed information
    for value in required_values:
        if value not in payload:
            return jsonify({'error': 'Invalid payload arguments'})

    statement = """insert into users(email, password, username) values(%s, %s, %s) returning user_id"""

    # Values to complete the statement
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
    """
    ROUTE (PUT): /dbproj/user

    Authenticates the given user and gets the auth token

    :return: Auth token or an error if something went wrong
    """

    # Payload with the user information
    payload = request.get_json()

    required_values = ['username', 'password']

    # Check if the payload contains all of the needed information
    for value in required_values:
        if value not in payload:
            return jsonify({'error': 'Invalid payload arguments'})

    connection = db_connection()
    cursor = connection.cursor()

    statement = """select user_id from users where username = %s and password = %s """

    # Values to complete the statement
    values = (payload['username'], payload['password'])

    try:
        cursor.execute(statement, values)
        rows = cursor.fetchall()

        # Check if the user and the password were correct
        if len(rows) == 0:
            result = {"error": 'Incorrect username or password'}
        else:
            user_id = int(rows[0][0])
            
            token = encode_token(user_id)
            
            result = {"auth_token": token}

    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
        result = {"error": str(error)}
    finally:
        if connection is not None:
            connection.close()
    return jsonify(result)

