from flask import Blueprint, jsonify, request
import psycopg2
import sys
import datetime
sys.path.append('..')
from auth.auth_jwt import auth_token
from database.database import db_connection

auction = Blueprint('auction', __name__, url_prefix='/dbproj/auction' )

@auction.route('', methods=['POST'])
@auth_token
def create_auction(data):
    payload = request.get_json()
    
    required_values = ['item_id', 'min_price', 'title', 'description', 'end_date', 'item_name', 'item_description']
    
    for value in required_values:
        if value not in payload:
            return jsonify({'error': 'Invalid payload arguments'})

    try:
        float(payload['min_price'])
        datetime.datetime.strptime(payload['end_date'], "%Y-%m-%d %H:%M:%S")
    except Exception as e:
        print(e)
        return jsonify({'error': 'Couldn\'t convert the minimum bid price or end date'})

    connection = db_connection()
    cursor = connection.cursor() 

    statement = """insert into auctions (item_id, min_price, title, description	, auctioneer_id, end_date, creation_date, item_name, item_description, ended) 
                        values (%s, %s, %s, %s, %s, %s, current_timestamp, %s, %s, false) returning auction_id"""
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

@auction.route('/<auction_id>', methods=['GET'])
def get_auction_info(auction_id):
    connection = db_connection()
    cursor = connection.cursor()
    
    try:
        auction_id = int(auction_id)
    except:
        return jsonify({'error': 'Couldn\'t convert auction id'})

    statement = """select auction_id, description, item_id, item_name, item_description from auctions where auction_id = %s"""
    statement_messages = """select message_id, body, date, sender_id from messages where auction_id = %s"""
    statement_history = """select description, title, modified_date from auction_history where auction_id = %s"""

    values = (auction_id,)

    try:
        cursor.execute(statement, values)
        auction_rows = cursor.fetchall()

        cursor.execute(statement_messages, values)
        messages_rows = cursor.fetchall()

        cursor.execute(statement_history, values)
        history_rows = cursor.fetchall()

        messages =  [{
                    'message_id': message_id,
                    'body': message_body,
                    'date': date,
                    'sender_id': sender_id
                    } for message_id, message_body, date, sender_id in messages_rows]

        history =   [{
                    'description': description,
                    'title': title,
                    'modified_date': modified_date
                    } for description, title, modified_date in history_rows]

        result =    [{
                    'auction_id': auction_id,
                    'description': description,
                    'item_id': item_id,
                    'item_name': item_name,
                    'item_description': item_description,
                    'messages': messages,
                    'history': history
                    } for auction_id, description, item_id, item_name, item_description in auction_rows]
    except (Exception, psycopg2.DatabaseError) as error:
        result = {"error": str(error)}
    finally:
        if connection is not None:
            connection.close()
    
    return jsonify(result)

@auction.route('/<auction_id>', methods=['PUT'])
@auth_token
def edit_auction(data, auction_id):
    payload = request.get_json()
    connection = db_connection()
    cursor = connection.cursor()

    try:
        auction_id = int(auction_id)
    except:
        return jsonify({'error': 'Couldn\'t convert auction id'})
    
    user_id = data['user_id']

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
            result =  { 'auction_id': int(rows[0][0]), 
                        'min_price': float(rows[0][1]),
                        'title': rows[0][2],
                        'description': rows[0][3],
                        'end_date': rows[0][4],
                        'creation_date': rows[0][5],
                        'item_id': rows[0][6],
                        'item_name': rows[0][7],
                        'item_description': rows[0][8],
                        'auctioneer_id': int(rows[0][9]),
                        'winning_bid': int(rows[0][10])}
    except (Exception, psycopg2.DatabaseError) as error:
        result = {"error": str(error)}
    finally:
        if connection is not None:
            connection.close()

    return jsonify(result)


@auction.route('/end', methods=['PUT'])
def end_auction():
    connection = db_connection()
    cursor = connection.cursor()
    #TODO: ver se funcemina
    statement = """
                update auctions set ended = true where end_date < current_timestamp and ended = false returning auction_id, winning_bid, auctioneer_id
                """
    
    statement_insert_winner =   """
                                insert into notifications (title, body, send_date, receiver_id)
                                values('AUCTION ENDED', 'Auction %s ended. You had the highest bid =D', current_timestamp, %s)
                                """

    statement_insert_owner =    """
                                insert into notifications (title, body, send_date, receiver_id)
                                values('AUCTION ENDED', 'Your auction %s ended with a highest bid of %s $', current_timestamp, %s)
                                """

    statement_get_winner =  """
                            select bidder_id, money from biddings where bidding_id = %s
                            """
    try:
        cursor.execute(statement)
        rows = cursor.fetchall()
        if len(rows) > 0:
            for auction_id, winning_bid, auctioneer_id in rows:
                money = 0
                if winning_bid is not None:
                    cursor.execute(statement_get_winner, (winning_bid,))
                    winning_bid_data = cursor.fetchall()
                    winner_id = winning_bid_data[0][0]
                    money = winning_bid_data[0][1]
                    cursor.execute(statement_insert_winner, (auction_id, winner_id))
                cursor.execute(statement_insert_owner, (auction_id, money, auctioneer_id))
                
        cursor.execute('commit')
        result = {"result": "success"}
    except (Exception, psycopg2.DatabaseError) as error:
        result = {"error": str(error)}
    finally:
        if connection is not None:
            connection.close()

    return jsonify(result)
