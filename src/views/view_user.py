"""
    :title: Smart Auction Project 
    :subject: BD 2020/2021
    :authors: Joana Simoes - 2019217013, Samuel Carinhas - 2019217199
"""

import psycopg2
from flask import Blueprint, jsonify, request
from auth.auth_jwt import encode_token, generate_hash, check_password
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
    values = (payload['email'], generate_hash(payload['password']), payload['username'])

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

    statement = """select user_id, password from users where username = %s """

    # Values to complete the statement
    values = (payload['username'],)

    try:
        cursor.execute(statement, values)
        rows = cursor.fetchall()

        # Check if the user and the password were correct
        if len(rows) == 0:
            result = {"error": 'Username not found'}
        else:
            user_id = int(rows[0][0])
            hash_password = rows[0][1]

            if check_password(payload['password'], hash_password):
                token = encode_token(user_id)
                result = {"auth_token": token}
            else:
                result = {"error": 'Wrong password'}
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
        result = {"error": str(error)}
    finally:
        if connection is not None:
            connection.close()
    return jsonify(result)

