"""
    :title: Smart Auction Project 
    :subject: BD 2020/2021
    :authors: Joana Simoes - 2019217013, Samuel Carinhas - 2019217199
"""

import psycopg2
from flask import Blueprint, jsonify
from auth.auth_jwt import auth_token
from database.database import db_connection


notifications = Blueprint('notifications', __name__, url_prefix='/dbproj/notifications')


@notifications.route('', methods=['GET'])
@auth_token
def see_notifications(data):
    """
    ROUTE (GET): /dbproj/notifications

    Read the unread notifications and update the received data

    :param data: Decoded token from auth_token function
    :return: Unread notifications or an error if something went wrong
    """
    connection = db_connection()
    cursor = connection.cursor()

    statement = """
                select title, body, send_date
                from notifications where receiver_id = %s and received_date is null
                """

    # Values to complete the statement
    values = (data['user_id'],)

    statement_update =  """
                        update notifications set received_date = current_timestamp
                        where receiver_id = %s and received_date is null
                        """

    try:
        cursor.execute(statement, values)
        rows = cursor.fetchall()

        # List of unread notifications
        notifs =    [{
                        'title': title,
                        'body': body,
                        'send_date': send_date
                    } for title, body, send_date in rows]
        
        cursor.execute(statement_update, values);
        
        cursor.execute('commit')
        
        result = {"notifications": notifs}
    except (Exception, psycopg2.DatabaseError) as error:
        result = {"error": str(error)}
    finally:
        if connection is not None:
            connection.close()

    return jsonify(result)
