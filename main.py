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
                        values (%s, %s, %s, %s, %s, %s, current_timestamp, %s, %s) returning auction_id"""
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
    statement_messages = """select message_id, body, date, sender_id from messages where auction_id = %s"""
    
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
                    'body': message_body,
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


@app.route('/dbproj/activity', methods=['GET'])
@token_required
def get_user_activity(data):
    connection = db_connection()
    cursor = connection.cursor()

    statement = """ select auction_id, description
                    from auctions
                    where auctioneer_id = %s
                    or exists (
                        select auction_id
                        from biddings
                        where
                        biddings.auction_id = auctions.auction_id
                        and
                        biddings.bidder_id = auctions.auctioneer_id
                    ) """
    
    values = (data['user_id'],)
    
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


@app.route('/dbproj/bid/<auction_id>/<bidding_value>', methods = ['GET'])
@token_required
def place_bidding(data, auction_id, bidding_value):
    bidding_value = float(bidding_value)

    connection = db_connection()
    cursor = connection.cursor()
    
    
    statement_verify =  """
                        select
                        coalesce((
                            select money
                            from biddings
                            where bidding_id = auctions.winning_bid)
                        , min_price)
                        from auctions
                        where auction_id = %s
                        and end_date > current_timestamp
                        """
    
    values_verify = (auction_id,)
    user_id = data['user_id']
    # TODO: Colocar um trigger aqui?

    try:
        cursor.execute(statement_verify, values_verify)
        rows = cursor.fetchall()
        if len(rows) == 0:
            result = {'error': 'Auction not found or has expired'}
        else:
            min_bid = float(rows[0][0])
            if bidding_value > min_bid:
                statement_insert =  """
                                    insert into biddings(money, date, bidder_id, auction_id)
                                    values(%s, current_timestamp, %s, %s) returning bidding_id
                                    """
                values_insert = (bidding_value, user_id, auction_id)
                cursor.execute(statement_insert, values_insert)
                rows = cursor.fetchall()
                winning_bid = rows[0][0]
                statement_update =  """
                                    update auctions set winning_bid = %s where auctions.auction_id = %s
                                    """
                values_update = (winning_bid, auction_id)
                cursor.execute(statement_update, values_update)
                cursor.execute('commit')
                result = {'result': 'Success'}
            else:
                result = {'error': 'Invalid bid'}
    except (Exception, psycopg2.DatabaseError) as error:
        result = {"error": str(error)}
    finally:
        if connection is not None:
            connection.close()

    return jsonify(result)


@app.route('/dbproj/auction/<auction_id>', methods=['PUT'])
@token_required
def edit_auction(data, auction_id):
    payload = request.get_json()
    connection = db_connection()
    cursor = connection.cursor()

    user_id = data['user_id']

    #TODO:trigger
    if 'title' in payload and 'description' in payload:
        statement = """
                    update auctions set title = %s, description = %s where auction_id = %s and auctioneer_id = %s
                    returning auction_id, min_price, title, description, end_date, creation_date, item_id, item_name, item_description, auctioneer_id, winning_bid
                    """
        values = (payload['title'], payload['description'], auction_id, user_id)
    elif 'title' in payload:
        statement = """
                    update auctions set title = %s where auction_id = %s and auctioneer_id = %s
                    returning auction_id, min_price, title, description, end_date, creation_date, item_id, item_name, item_description, auctioneer_id, winning_bid
                    """
        values = (payload['title'], auction_id, user_id)
    elif 'description' in payload:
        statement = """
                    update auctions set description = %s where auction_id = %s and auctioneer_id = %s
                    returning auction_id, min_price, title, description, end_date, creation_date, item_id, item_name, item_description, auctioneer_id, winning_bid
                    """
        values = (payload['description'], auction_id, user_id)
    else:
        return jsonify({'error': 'Invalid payload'})

    try:
        cursor.execute(statement, values)
        rows = cursor.fetchall()

        if len(rows) == 0:
            result = {'error': 'Auction not found or permission denied'}
        else:
            cursor.execute('commit')
            result =  { 'auction_id': rows[0][0], 
                        'min_price': rows[0][1],
                        'title': rows[0][2],
                        'description': rows[0][3],
                        'end_date': rows[0][4],
                        'creation_date': rows[0][5],
                        'item_id': rows[0][6],
                        'item_name': rows[0][7],
                        'item_description': rows[0][8],
                        'auctioneer_id': rows[0][9],
                        'winning_bid': rows[0][10]}
    except (Exception, psycopg2.DatabaseError) as error:
        result = {"error": str(error)}
    finally:
        if connection is not None:
            connection.close()

    return jsonify(result)


@app.route('/dbproj/message', methods=['POST'])
@token_required
def new_message(data):
    payload = request.get_json()
    connection = db_connection()
    cursor = connection.cursor()
    user_id = data['user_id']
    statement = """
                insert into messages (body, date, auction_id, sender_id) values(%s, current_timestamp, %s, %s) returning message_id
                """
    values = (str(payload['body']), str(payload['auction_id']), str(user_id))
    try:
        cursor.execute(statement, values)
        rows = cursor.fetchall()
        cursor.execute('commit')
        result = {'message_id': str(rows[0][0])}
    except (Exception, psycopg2.DatabaseError) as error:
        result = {"error": str(error)}
    finally:
        if connection is not None:
            connection.close()

    return jsonify(result)


def main():
    print('\n-----------------------------------\nSmart Action started\n-----------------------------------\n')
    app.run(host="localhost", debug=True, threaded=True)


if __name__ == '__main__':
    main()
