import pymysql
from flask import current_app

def get_db():
    # A simple way: create new connection every time (less optimal for high traffic)
    connection = pymysql.connect(
        host=current_app.config["DB_HOST"],
        user=current_app.config["DB_USER"],
        password=current_app.config["DB_PASSWORD"],
        db=current_app.config["DB_NAME"],
        port=current_app.config["DB_PORT"],
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor
    )
    return connection
