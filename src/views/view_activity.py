from flask import Blueprint, jsonify, request
import psycopg2
import sys
sys.path.append('..')
from auth.auth_jwt import auth_token
from database.database import db_connection


activity = Blueprint('activity', __name__, url_prefix='/dbproj/activity')


@activity.route('', methods=['GET'])
@auth_token
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
