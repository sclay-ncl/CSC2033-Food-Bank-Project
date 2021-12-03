from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

app.config['SQLALCHEMY_DATABASE_URI'] = \
     'mariadb+mariadbconnector://csc2033_team15:Pea5NudeCure@127.0.0.1:8989/csc2033_team15'

db = SQLAlchemy(app)


@app.route('/')
def hello_world():  # put application's code here
    return 'Hello World!'


if __name__ == '__main__':
    app.run()
