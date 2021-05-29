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
    bidding_value = float(bidding_value)

    connection = db_connection()
    cursor = connection.cursor()

    statement_verify_user = """
                select auctioneer_id
                from auctions
                where auction_id = %s
                """
   
    
    values_verify = (auction_id,)

    user_id = data['user_id']
    # TODO: Colocar um trigger aqui?

    try:
        cursor.execute(statement_verify_user, values_verify)
        rows = cursor.fetchall()
        if user_id != rows[0][0]:
            statement_verify_bid =  """
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
            cursor.execute(statement_verify_bid, values_verify)
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
        else:
            result = {'error': 'The auction owner cannot bid'}
    except (Exception, psycopg2.DatabaseError) as error:
        result = {'error': str(error)}
    finally:
        if connection is not None:
            connection.close()

    return jsonify(result)