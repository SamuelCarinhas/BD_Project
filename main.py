from flask import Flask, jsonify, request
import logging, psycopg2, time, json
import jwt
from functools import wraps
import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = 'weeeeeeeeeeeeeeeeeeeeeeeee'


def load_config():
    with open('config/config.json', 'r') as config:
        return json.load(config)


def db_connection():
    config = load_config()
    db = psycopg2.connect(user=config['user'],
                          password=config['password'],
                          host=config['host'],
                          port=config['port'],
                          database=config['database'])
    return db


def token_required(f):
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
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
        except:
            return jsonify({'error' : 'Token is invalid!'})

        return f(data, *args, **kwargs)

    return decorated



@app.route('/dbproj/user', methods=['POST'])
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


@app.route('/dbproj/user', methods=['PUT'])
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
            token = jwt.encode({'user_id' : user_id, 'exp' : datetime.datetime.utcnow() + datetime.timedelta(minutes=30)}, app.config['SECRET_KEY'], algorithm="HS256")
            result = {"auth_token": token}

    except (Exception, psycopg2.DatabaseError) as error:
        result = {"error": str(error)}
    finally:
        if connection is not None:
            connection.close()
    return jsonify(result)


@app.route('/dbproj/auctions', methods=['POST'])
@token_required
def create_auction(data):
    payload = request.get_json()

    connection = db_connection()
    cursor = connection.cursor() 

    statement = """insert into auctions (item_id, min_price, title, description	, auctioneer_id, end_date, creation_date, item_name, item_description) 
                        values (%s, %s, %s, %s, %s, %s, current_date, %s, %s) returning auction_id"""
    values = (payload['item_id'], payload['min_price'], payload['title'], payload['description'], data['user_id'], payload['end_date'], payload['item_name'], payload['item_description'])

    try:
        cursor.execute(statement, values)
        rows = cursor.fetchall()
        cursor.execute('commit')
        result = {"auction_id" : int(rows[0][0])}
    except (Exception, psycopg2.DatabaseError) as error:
        result = {"error": str(error)}
    finally:
        if connection is not None:
            connection.close()
    return jsonify(result)


@app.route('/dbproj/auctions', methods=['GET'])
def get_auctions():
    connection = db_connection()
    cursor = connection.cursor()
    
    try:
        cursor.execute('select auction_id, description from auctions')
        rows = cursor.fetchall()
        result = [{'auction_id': int(auction_id), 'description': str(description)} for auction_id, description in rows]
    except (Exception, psycopg2.DatabaseError) as error:
        result = {"error": str(error)}
    finally:
        if connection is not None:
            connection.close()
    return jsonify(result)


@app.route('/dbproj/auctions/<keyword>', methods=['GET'])
def search_auctions_by_item(keyword):
    connection = db_connection()
    cursor = connection.cursor()

    statement = """select auction_id, description from auctions where item_id = %s or lower(item_description) like lower(%s)"""
    values = (keyword, '%%' + str(keyword) + '%%')
    try:
        cursor.execute(statement, values)
        rows = cursor.fetchall()
        result = [{'auction_id': int(auction_id), 'description': str(description)} for auction_id, description in rows]
    except (Exception, psycopg2.DatabaseError) as error:
        result = {"error": str(error)}
    finally:
        if connection is not None:
            connection.close()
    return jsonify(result)
        


@app.route('/dbproj/auction/<auction_id>', methods=['GET'])
def get_auction_info(auction_id):
    connection = db_connection()
    cursor = connection.cursor()

    statement = """select auction_id, description, item_id, item_name, item_description from auctions where auction_id = %s"""
    statement_messages = """select message_id, message_body, date, sender_id from messages where auction_id = %s"""
    
    values = (auction_id,)

    try:
        cursor.execute(statement, values)
        auction_rows = cursor.fetchall()

        cursor.execute(statement_messages, values)
        messages_rows = cursor.fetchall()

        print(auction_rows)
        print(messages_rows)

        messages =  [{
                    'message_id': message_id,
                    'message_body': message_body,
                    'date': date,
                    'sender_id': sender_id
                    } for message_id, message_body, date, sender_id in messages_rows]

        result =    [{
                    'auction_id': auction_id,
                    'description': description,
                    'item_id': item_id,
                    'item_name': item_name,
                    'item_description': item_description,
                    'messages': messages
                    } for auction_id, description, item_id, item_name, item_description in auction_rows]
    except (Exception, psycopg2.DatabaseError) as error:
        result = {"error": str(error)}
    finally:
        if connection is not None:
            connection.close()
    
    return jsonify(result)


def main():
    print('\n-----------------------------------\nSmart Action started\n-----------------------------------')
    app.run(host="localhost", debug=True, threaded=True)


if __name__ == '__main__':
    main()
