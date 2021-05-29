from flask import request
import jwt
import datetime
from functools import wraps


SECRET_KEY = 'WEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEE'


def auth_token(f):
    '''
    https://www.youtube.com/watch?v=J5bIPtEbS0Q
    :return:
    '''
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.args.get('auth_token')

        if not token:
            return jsonify({'error' : 'Token is missing!'})
        try: 
            data = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        except:
            return jsonify({'error' : 'Token is invalid!'})

        return f(data, *args, **kwargs)

    return decorated


def encode_token(user_id):
    return jwt.encode({'user_id' : user_id, 'exp' : datetime.datetime.utcnow() + datetime.timedelta(minutes=30)}, SECRET_KEY, algorithm="HS256")
