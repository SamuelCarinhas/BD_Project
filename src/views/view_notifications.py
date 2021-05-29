from flask import Blueprint, jsonify, request
import psycopg2
import sys
sys.path.append('..')
from auth.auth_jwt import auth_token, encode_token
from database.database import db_connection


notifications = Blueprint('notifications', __name__, url_prefix='/dbproj/notifications')


@notifications.route('', methods=['GET'])
@auth_token
def see_notifications(data):
    connection = db_connection()
    cursor = connection.cursor()

    statement = """select title, body, send_date from notifications where receiver_id = %s and received_date is null"""
    values = (data['user_id'],)

    statement_update = """update notifications set received_date = current_timestamp where receiver_id = %s and received_date is null"""

    try:
        cursor.execute(statement, values)
        rows = cursor.fetchall()

        notifications = [{
                        'title': title,
                        'body': body,
                        'send_date': send_date
                        } for title, body, send_date in rows]
        
        cursor.execute(statement_update, values);
        
        cursor.execute('commit')
        
        result = {"notifications": notifications}
    except (Exception, psycopg2.DatabaseError) as error:
        result = {"error": str(error)}
    finally:
        if connection is not None:
            connection.close()

    return jsonify(result)
