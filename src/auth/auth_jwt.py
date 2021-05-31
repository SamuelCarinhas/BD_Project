"""
    :title: Smart Auction Project 
    :subject: BD 2020/2021
    :authors: Joana Simoes - 2019217013, Samuel Carinhas - 2019217199
"""

import bcrypt, jwt, datetime
from flask import request, jsonify
from functools import wraps


# Secret key to encode and decode the auth tokens
SECRET_KEY = ''


def setup_secret(secret):
    """
    Update the current SECRET_KEY

    :param secret: SECRET_KEY to encode and decode the tokens
    :return: None
    """
    global SECRET_KEY
    SECRET_KEY = secret


def auth_token(f):
    """
    Validates the user's token and if its valid calls the given function
    Addapted form: https://www.youtube.com/watch?v=J5bIPtEbS0Q

    :param f: Fuction that requires the token
    :return: Json error if the token is invalid, otherwise returns the function's result
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.args.get('auth_token')

        if not token:
            return jsonify({'error': 'Auth token is missing!'})
        try:
            data = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        except:
            return jsonify({'error': 'Auth token is invalid!'})

        return f(data, *args, **kwargs)

    return decorated


def encode_token(user_id):
    """
    Creates a token for the given user

    :param user_id: User identification number
    :return: Json with the token
    """
    return jwt.encode({'user_id': user_id, 'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=30)},
                      SECRET_KEY, algorithm="HS256")


def generate_hash(password):
    # https://pypi.org/project/bcrypt/
    return bcrypt.hashpw(password, bcrypt.gensalt(8))


def check_password(password, password_hash):
    # https://pypi.org/project/bcrypt/
    return bcrypt.checkpw(password, password_hash)
