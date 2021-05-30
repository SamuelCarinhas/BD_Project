"""
    :title: Smart Auction Project 
    :subject: BD 2020/2021
    :authors: Joana Simoes - 2019217013, Samuel Carinhas - 2019217199
"""

import psycopg2


# Database configuration
db_config = {}


def setup_dbconfig(config):
    """
    Update the current db_config

    :param config: Json with the configuration needed to connect to the database
    :return: None
    """
    global db_config
    db_config = config


def db_connection():
    """
    Connects to the database from the config

    :return: Database connection
    """
    db = psycopg2.connect(user=db_config['user'],
                          password=db_config['password'],
                          host=db_config['host'],
                          port=db_config['port'],
                          database=db_config['database'])
    return db
