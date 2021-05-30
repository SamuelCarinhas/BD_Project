import psycopg2
from flask import Blueprint, jsonify, request
from auth.auth_jwt import auth_token
from database.database import db_connection


# Blueprint with prefix
message = Blueprint('message', __name__, url_prefix='/dbproj/message')


@message.route('', methods=['POST'])
@auth_token
def new_message(data):
    """
    ROUTE (POST): /dbproj/message

    Post a message in give auction's blog

    :param data: Decoded token from auth_token function
    :return: Message id if the message was posted successefully, otherwise returns some error
    """

    # Payload with the auction_id and the message's body
    payload = request.get_json()

    required_values = ['body', 'auction_id']

    # Check if the payload have the needed information
    for value in required_values:
        if value not in payload:
            return jsonify({'error': 'Invalid payload arguments'})

    connection = db_connection()
    cursor = connection.cursor()

    # User id from token
    user_id = data['user_id']

    try:
        payload['auction_id'] = int(payload['auction_id'])
    except:
        return jsonify({'error': 'Couldn\'t convert auction id'})

    statement = """
                insert into messages (body, date, auction_id, sender_id)
                values(%s, current_timestamp, %s, %s)
                returning message_id
                """

    # Values to complete the statement
    values = (str(payload['body']), str(payload['auction_id']), str(user_id))

    try:
        cursor.execute(statement, values)
        rows = cursor.fetchall()
        cursor.execute('commit')
        result = {'message_id': int(rows[0][0])}
    except (Exception, psycopg2.DatabaseError) as error:
        result = {"error": str(error)}
    finally:
        if connection is not None:
            connection.close()

    return jsonify(result)
