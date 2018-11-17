import mysql.connector
from flask import g
from app import config

# connect to database
def connect_to_database():
    return mysql.connector.connect(user=config.db_config['user'],
                                   password=config.db_config['password'],
                                   host=config.db_config['host'],
                                   port=config.db_config['port'],
                                   database=config.db_config['database'])

# init the database
def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = connect_to_database()
    return db
