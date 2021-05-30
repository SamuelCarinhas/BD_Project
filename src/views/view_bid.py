"""
    :title: Smart Auction Project 
    :subject: BD 2020/2021
    :authors: Joana Simoes - 2019217013, Samuel Carinhas - 2019217199
"""

import psycopg2
from flask import Blueprint, jsonify
from auth.auth_jwt import auth_token
from database.database import db_connection


# Blueprint with prefix
bid = Blueprint('bid', __name__, url_prefix='/dbproj/bid')


@bid.route('/<auction_id>/<bidding_value>', methods=['GET'])
@auth_token
def place_bidding(data, auction_id, bidding_value):
    """
    ROUTE (GET): /dbproj/bid/<auction_id>/<bidding_value>

    Place a bid in a given auction with the given ammount

    :param data: Decoded token from auth_token function
    :param auction_id: Auction id to place the bid
    :param bidding_value: Bid monetary value
    :return: Success if the bill was placed, otherwise returns some error
    """

    # Verify if the given arguments are correct
    try:
        bidding_value = float(bidding_value)
        auction_id = int(auction_id)
    except:
        return jsonify({'error': 'Couldn\'t convert the given arguments'})

    connection = db_connection()
    cursor = connection.cursor()

    statement_verify_user = """
                            select auctioneer_id
                            from auctions
                            where auction_id = %s
                            """

    # Values to complete the statement
    values_verify = (auction_id,)

    # User_id from token
    user_id = data['user_id']

    try:
        cursor.execute(statement_verify_user, values_verify)
        rows = cursor.fetchall()

        # Check if the auction exists in the database
        if len(rows) == 0:
            return jsonify({'error': 'Auction not found'})

        # Check if the bidder is not the auction's owner
        if user_id != rows[0][0]:
            statement_verify_bid =  """
                                    select end_date >= current_timestamp
                                    from auctions
                                    where auction_id = %s
                                    """
            cursor.execute(statement_verify_bid, values_verify)
            rows = cursor.fetchall()

            running = bool(rows[0][0])

            # Check if the auction is running
            if running:
                statement_insert =  """
                                    insert into biddings(money, date, bidder_id, auction_id)
                                    values(%s, current_timestamp, %s, %s) returning bidding_id
                                    """

                # Values to complete the statement
                values_insert = (bidding_value, user_id, auction_id)
                cursor.execute(statement_insert, values_insert)
                rows = cursor.fetchall()
                winning_bid = rows[0][0]
                
                statement_update =  """
                                    update auctions set winning_bid = %s where auctions.auction_id = %s and coalesce((
                                    select money
                                    from biddings
                                    where bidding_id = auctions.winning_bid)
                                    , min_price) < %s
                                    """
                values_update = (winning_bid, auction_id, bidding_value)
                cursor.execute(statement_update, values_update)

                # Check if the bid was placed correctly
                if cursor.rowcount == 0:
                    result = {'error': 'You need to make an higher bid'}
                    cursor.execute('rollback')
                else:
                    result = {'result': 'Success'}
                    cursor.execute('commit')
            else:
                result = {'error': 'This auction has already ended'}
        else:
            result = {'error': 'The auction owner cannot place a bid'}
    except (Exception, psycopg2.DatabaseError) as error:
        result = {'error': str(error)}
    finally:
        if connection is not None:
            connection.close()

    return jsonify(result)
