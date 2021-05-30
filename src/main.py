"""
    :title: Smart Auction Project 
    :subject: BD 2020/2021
    :authors: Joana Simoes - 2019217013, Samuel Carinhas - 2019217199
"""

import json, views
from flask import Flask
from database.database import setup_dbconfig
from auth.auth_jwt import setup_secret


# Create flask app
app = Flask(__name__)


def load_config():
    """
    Loads database login configuration from config json file and
    secret key from token encoding from token json file
    :return: True if the config is valid, otherwise returns False
    """
    with open('../config/config.json', 'r') as config:
        config_json = json.load(config)
        required_values = ['user', 'password', 'host', 'port', 'database']
        for value in required_values:
            if value not in config_json:
                return False
        setup_dbconfig(config_json)

    with open('../config/token.json', 'r') as token:
        token_json = json.load(token)
        if 'SECRET_KEY' not in token_json:
            return False
        setup_secret(token_json['SECRET_KEY'])

    return True


def main():
    """
    Main function
    Register the flask blueprints and run the flask app
    :return: None
    """
    if not load_config():
        print('Error loading config files...')
        exit(-1)

    app.register_blueprint(views.activity)
    app.register_blueprint(views.auction)
    app.register_blueprint(views.auctions)
    app.register_blueprint(views.bid)
    app.register_blueprint(views.message)
    app.register_blueprint(views.user)
    app.register_blueprint(views.notifications)

    print('\n-----------------------------------\nSmart Action started\n-----------------------------------\n')

    app.run(host="localhost", debug=True, threaded=True)


# Calls the main function
if __name__ == '__main__':
    main()
