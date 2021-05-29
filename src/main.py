from flask import Flask, jsonify, request
from database.database import setup_dbconfig
import json
import jwt
import datetime
import views


app = Flask(__name__)


def load_config():
    config = {}
    with open('../config/config.json', 'r') as config:
        setup_dbconfig(json.load(config))


def main():
    load_config()

    app.register_blueprint(views.activity)
    app.register_blueprint(views.auction)
    app.register_blueprint(views.auctions)
    app.register_blueprint(views.bid)
    app.register_blueprint(views.message)
    app.register_blueprint(views.user)

    print('\n-----------------------------------\nSmart Action started\n-----------------------------------\n')

    app.run(host="localhost", debug=True, threaded=True)


if __name__ == '__main__':
    main()
