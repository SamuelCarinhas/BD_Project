from flask import Blueprint, jsonify, request
import psycopg2
import sys
sys.path.append('..')
from auth.auth_jwt import auth_token
from database.database import db_connection


bid = Blueprint('bid', __name__, url_prefix='/dbproj/bid')


@bid.route('/<auction_id>/<bidding_value>', methods = ['GET'])
@auth_token
def place_bidding(data, auction_id, bidding_value):
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

    values_verify = (auction_id,)
    user_id = data['user_id']

    try:
        cursor.execute(statement_verify_user, values_verify)
        rows = cursor.fetchall()

        if len(rows) == 0:
            return jsonify({'error': 'Auction not found'})

        if user_id != rows[0][0]:
            statement_verify_bid =  """
                                    select end_date >= current_timestamp
                                    from auctions
                                    where auction_id = %s
                                    """
            cursor.execute(statement_verify_bid, values_verify)
            rows = cursor.fetchall()

            running = bool(rows[0][0])
            if running:
                statement_insert =  """
                                    insert into biddings(money, date, bidder_id, auction_id)
                                    values(%s, current_timestamp, %s, %s) returning bidding_id
                                    """
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