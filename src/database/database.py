import psycopg2


db_config = {}


def setup_dbconfig(config):
    global db_config
    db_config = config


def db_connection():
    db = psycopg2.connect(user=db_config['user'],
                          password=db_config['password'],
                          host=db_config['host'],
                          port=db_config['port'],
                          database=db_config['database'])
    return db