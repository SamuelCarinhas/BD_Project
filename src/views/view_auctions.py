"""
    :title: Smart Auction Project 
    :subject: BD 2020/2021
    :authors: Joana Simoes - 2019217013, Samuel Carinhas - 2019217199
"""

import psycopg2
from flask import Blueprint, jsonify
from database.database import db_connection


# Blueprint with prefix
auctions = Blueprint('auctions', __name__, url_prefix='/dbproj/auctions')


@auctions.route('', methods=['GET'])
def get_auctions():
    """
    ROUTE (GET): /dbproj/auctions

    Get all auctions from the database

    :return: Auction list, or some error if something went wrong
    """
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


@auctions.route('/<keyword>', methods=['GET'])
def search_auctions_by_item(keyword):
    """
    ROUTE (GET): /dbproj/auctions/<keyword>

    Get all auctions from the database where the given keyword
    is equal to some item_id or is contained in the item_description

    :param keyword: Keyword to use in search query
    :return: Auction list, or some error if something went wrong
    """
    connection = db_connection()
    cursor = connection.cursor()

    statement = """
                select auction_id, description
                from auctions
                where item_id = %s or lower(item_description) like lower(%s)
                """

    # Values to complete the statement
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


@auctions.route('/end', methods=['PUT'])
def end_auction():
    """
    ROUTE (PUT): /dbproj/auctions/end

    Searches for auctions that have already expired, updates
    their info to "ended" and notifies the winner and the auctioneer
    
    :return:
    """
    connection = db_connection()
    cursor = connection.cursor()
    # statement to update the auctions info to ended when they have expired
    statement = """
                update auctions set ended = true
                where end_date < current_timestamp and ended = false
                returning auction_id, winning_bid, auctioneer_id
                """
    # notifies the winner
    statement_insert_winner =   """
                                insert into notifications (title, body, send_date, receiver_id)
                                values('AUCTION ENDED', 'Auction %s ended. You had the highest bid =D', current_timestamp, %s)
                                """
    # notifies the auctioneer
    statement_insert_owner =    """
                                insert into notifications (title, body, send_date, receiver_id)
                                values('AUCTION ENDED', 'Your auction %s ended with a highest bid of %s $', current_timestamp, %s)
                                """
    # search for the winning bidder
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

