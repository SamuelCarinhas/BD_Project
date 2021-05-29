from flask import Blueprint, jsonify, request
import psycopg2
import sys
sys.path.append('..')
from auth.auth_jwt import auth_token
from database.database import db_connection

message = Blueprint('message', __name__, url_prefix='/dbproj/message')

@message.route('', methods=['POST'])
@auth_token
def new_message(data):
    payload = request.get_json()
    connection = db_connection()
    cursor = connection.cursor()
    user_id = data['user_id']
    statement = """
                insert into messages (body, date, auction_id, sender_id) values(%s, current_timestamp, %s, %s) returning message_id
                """
    values = (str(payload['body']), str(payload['auction_id']), str(user_id))
    try:
        cursor.execute(statement, values)
        rows = cursor.fetchall()
        cursor.execute('commit')
        result = {'message_id': str(rows[0][0])}
    except (Exception, psycopg2.DatabaseError) as error:
        result = {"error": str(error)}
    finally:
        if connection is not None:
            connection.close()

    return jsonify(result)