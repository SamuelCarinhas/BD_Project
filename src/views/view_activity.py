import psycopg2
from flask import Blueprint, jsonify
from auth.auth_jwt import auth_token
from database.database import db_connection


# Blueprint with prefix
activity = Blueprint('activity', __name__, url_prefix='/dbproj/activity')


@activity.route('', methods=['GET'])
@auth_token
def get_user_activity(data):
    """
    ROUTE (GET): /dbproj/activity

    Get auctions where the owner is the user or when the user
    placed at least one bid

    :param data: Decoded token from auth_token function
    :return: Auction list, or some error if something went wrong
    """
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
                        biddings.bidder_id = %s
                    ) """

    # Values to complete the statement
    values = (data['user_id'], data['user_id'])

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
