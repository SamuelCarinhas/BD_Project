from flask import Flask, jsonify, request
import logging, psycopg2, time, json

app = Flask(__name__)


def load_config():
    with open('config/config.json', 'r') as config:
        return json.load(config)


def db_connection():
    config = load_config()
    db = psycopg2.connect(user=config['user'],
                          password=config['password'],
                          host=config['host'],
                          port=config['port'],
                          database=config['database'])
    return db


@app.route('/dbproj/user', methods=['POST'])
def create_user():
    payload = request.get_json()

    connection = db_connection()
    cursor = connection.cursor()

    statement = """insert into utilizadores(email, password, username) values(%s, %s, %s) returning userid"""

    values = (payload['email'], payload['password'], payload['username'])

    try:
        cursor.execute(statement, values)
        rows = cursor.fetchall()

        cursor.execute('commit')

        result = '{"userId": %d}' % (rows[0][0])
    except (Exception, psycopg2.DatabaseError) as error:
        print('Something went wrong: %s' % (error))
        result = '{"error": "%s"}' % (error)
    finally:
        if connection is not None:
            connection.close()

    return result


@app.route('/dbproj/user', methods=['PUT'])
def authentication_user():
    content = request.get_json()

    connection = db_connection()
    cursor = connection.cursor()

    statement = """select userid from utilizadores where username = %s and password = %s """

    values = (content['username'], content['password'])

    try:
        cursor.execute(statement, values)
        if (cursor.rowcount==0):
            result = '{"error": "%s"}' % ('Not found')
        else:
            rows = cursor.fetchall()
            result = '{"authToken":%d}' % (rows[0][0])

    except (Exception, psycopg2.DatabaseError) as error:
        result = '{"error": "%s"}' % (error)
    finally:
        if connection is not None:
            connection.close()
    return result


@app.route('/dbproj/leilao', methods=['POST'])
def create_auction():
    payload = request.get_json()

    connection = db_connection()
    cursor = connection.cursor() 

    statement = """insert into leiloes (artigoId, precoMinimo, titulo, descricao, vendedorId, dataFim) 
                        values (%s, %s, %s, %s, %s, %s) returning leilaoId"""
    values = (payload['artigoId'], payload['precoMinimo'], payload['titulo'], payload['descricao'], payload['vendedorId'], payload['dataFim'])

    try:
        cursor.execute(statement, values)
        rows = cursor.fetchall()
        cursor.execute('commit')
        result = {"leilaoId" : rows[0][0]}
    except (Exception, psycopg2.DatabaseError) as error:
        result = '{"error": "%s"}' % (error)
    finally:
        if connection is not None:
            connection.close()
    return result


@app.route('/dbproj/leiloes', methods=['GET'])
def get_auctions():
    connection = db_connection()
    cursor = connection.cursor()
    
    try:
        cursor.execute('select leilaoId, descricao from leiloes')
        rows = cursor.fetchall()
        print(rows)
        result = '[' + ''.join('{"leilaoId": %s, "descricao": %s}'  % (leilaoId, descricao) for leilaoId, descricao in rows) + ']'
    except (Exception, psycopg2.DatabaseError) as error:
        result = '{"error": "%s"}' % (error)
    finally:
        if connection is not None:
            connection.close()
    return result

@app.route('/dbproj/leilao/<leilaoId>', methods=['GET'])
def get_auction_info(leilaoId):
    connection = db_connection()
    cursor = connection.cursor()

    try:
        cursor.execute("select ")
    except (Exception, psycopg2.DatabaseError) as error:
        result = '{"error": "%s"}' % (error)
    finally:
        if connection is not None:
            connection.close()


def main():
    print('\n-----------------------------------\nSmart Action started\n-----------------------------------')


if __name__ == '__main__':
    main()

    app.run(host="localhost", debug=False, threaded=True)
