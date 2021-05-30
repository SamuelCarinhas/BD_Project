"""
    :title: Smart Auction Project 
    :subject: BD 2020/2021
    :authors: Joana Simoes - 2019217013, Samuel Carinhas - 2019217199
"""

import psycopg2, datetime
from flask import Blueprint, jsonify, request
from auth.auth_jwt import auth_token
from database.database import db_connection


# Blueprint with prefix
auction = Blueprint('auction', __name__, url_prefix='/dbproj/auction')


@auction.route('', methods=['POST'])
@auth_token
def create_auction(data):
    """
    ROUTE (POST): /dbproj/auction

    Creates a new auction for the user

    :param data: Decoded token from auth_token function
    :return: Json with the new auction id if all goes well or with a error if something went wrong
    """
    payload = request.get_json()

    required_values = ['item_id', 'min_price', 'title', 'description', 'end_date', 'item_name', 'item_description']

    # Check if the payload have the needed information
    for value in required_values:
        if value not in payload:
            return jsonify({'error': 'Invalid payload arguments'})

    # Check if the given arguments are in the right format
    try:
        float(payload['min_price'])
        datetime.datetime.strptime(payload['end_date'], "%Y-%m-%d %H:%M:%S")
    except Exception as e:
        print(e)
        return jsonify({'error': 'Couldn\'t convert the minimum bid price or end date'})

    connection = db_connection()
    cursor = connection.cursor()

    # statement to add a new auction to the database
    statement = """insert into auctions (item_id, min_price, title, description	, auctioneer_id, end_date, creation_date, item_name, item_description, ended) 
                        values (%s, %s, %s, %s, %s, %s, current_timestamp, %s, %s, false)
                        returning auction_id"""

    # values to complete the statement
    values = (payload['item_id'], payload['min_price'], payload['title'], payload['description'], data['user_id'],
              payload['end_date'], payload['item_name'], payload['item_description'])

    try:
        cursor.execute(statement, values)
        rows = cursor.fetchall()
        cursor.execute('commit')
        result = {"auction_id": int(rows[0][0])}
    except (Exception, psycopg2.DatabaseError) as error:
        result = {"error": str(error)}
    finally:
        if connection is not None:
            connection.close()
    return jsonify(result)


@auction.route('/<auction_id>', methods=['GET'])
def get_auction_info(auction_id):
    """
    ROUTE (GET): /dbproj/auction/<auction_id>

    Get the auction info with that id

    :param auction_id: Auction identifier
    :return: Json with the auctions info or with a error if something went wrong
    """
    connection = db_connection()
    cursor = connection.cursor()
    # Checks if the received auction identifier is valid
    try:
        auction_id = int(auction_id)
    except:
        return jsonify({'error': 'Couldn\'t convert auction id'})

    # statement to get the auction info from the database
    statement = """
                select auction_id, description, item_id, item_name, item_description
                from auctions
                where auction_id = %s
                """
    # statement to get from the database the messages related with this auction
    statement_messages = """
                            select message_id, body, date, sender_id
                            from messages
                            where auction_id = %s
                            """
    # statement to get the history of changes of this auction from the database
    statement_history = """
                        select description, title, modified_date
                        from auction_history
                        where auction_id = %s"""

    # values to complete the statements
    values = (auction_id,)

    try:
        # get the auction info
        cursor.execute(statement, values)
        auction_rows = cursor.fetchall()

        if len(auction_rows) != 0:
            # get the messages
            cursor.execute(statement_messages, values)
            messages_rows = cursor.fetchall()
            # get the history
            cursor.execute(statement_history, values)
            history_rows = cursor.fetchall()

            messages = [{
                'message_id': message_id,
                'body': message_body,
                'date': date,
                'sender_id': sender_id
            } for message_id, message_body, date, sender_id in messages_rows]

            history = [{
                'description': description,
                'title': title,
                'modified_date': modified_date
            } for description, title, modified_date in history_rows]

            result = [{
                'auction_id': auction_id,
                'description': description,
                'item_id': item_id,
                'item_name': item_name,
                'item_description': item_description,
                'messages': messages,
                'history': history
            } for auction_id, description, item_id, item_name, item_description in auction_rows]
        else:
            result = {'error': 'Auction not found'}
    except (Exception, psycopg2.DatabaseError) as error:
        result = {"error": str(error)}
    finally:
        if connection is not None:
            connection.close()

    return jsonify(result)


@auction.route('/<auction_id>', methods=['PUT'])
@auth_token
def edit_auction(data, auction_id):
    """
    ROUTE (PUT): /dbproj/auction/<auction_id>

    Changes the info of the auction with the received identifier acoording to the parameters given by the
    payload

    :param data: Decoded token from auth_token function
    :param auction_id: AUction identifier
    :return: Json with the auction updated info or with a error
    """
    payload = request.get_json()
    connection = db_connection()
    cursor = connection.cursor()

    # Check if the auction_id can be converted to int
    try:
        auction_id = int(auction_id)
    except:
        return jsonify({'error': 'Couldn\'t convert auction id'})

    user_id = data['user_id']

    if 'title' in payload and 'description' in payload:
        # statement to update the auction title and description
        statement = """
                    update auctions set title = %s, description = %s where auction_id = %s and auctioneer_id = %s
                    returning auction_id, min_price, title, description, end_date, creation_date, item_id, item_name, item_description, auctioneer_id, winning_bid
                    """
        # values to complete the statement
        values = (payload['title'], payload['description'], auction_id, user_id)
    elif 'title' in payload:
        # statement to update the auction title 
        statement = """
                    update auctions set title = %s where auction_id = %s and auctioneer_id = %s
                    returning auction_id, min_price, title, description, end_date, creation_date, item_id, item_name, item_description, auctioneer_id, winning_bid
                    """
        # values to complete the statement
        values = (payload['title'], auction_id, user_id)
    elif 'description' in payload:
        # statement to update the auction description
        statement = """
                    update auctions set description = %s where auction_id = %s and auctioneer_id = %s
                    returning auction_id, min_price, title, description, end_date, creation_date, item_id, item_name, item_description, auctioneer_id, winning_bid
                    """
        # values to complete the statement
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
            result = {'auction_id': rows[0][0],
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
