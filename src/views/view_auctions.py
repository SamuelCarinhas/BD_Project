from flask import Blueprint, jsonify, request
import psycopg2
import sys
sys.path.append('..')
from auth.auth_jwt import auth_token
from database.database import db_connection

auctions = Blueprint('auctions', __name__, url_prefix='/dbproj/auctions')


@auctions.route('', methods=['GET'])
def get_auctions():
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
    connection = db_connection()
    cursor = connection.cursor()

    statement = """select auction_id, description from auctions where item_id = %s or lower(item_description) like lower(%s)"""
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
