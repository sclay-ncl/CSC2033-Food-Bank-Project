from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sshtunnel import SSHTunnelForwarder
import pymysql

app = Flask(__name__)

# ssh tunnel set up, untested until ssh servers are back up

# tunnel = SSHTunnelForwarder(
#     ssh_address_or_host='linux.cs.ncl.ac.uk',
#     ssh_username="username",
#     ssh_password='password',
#     remote_bind_address=('cs-db.ncl.ac.uk', 3306)
# )

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# app.config['SQLALCHEMY_DATABASE_URI'] = \
#     'mysql+pymysql:///csc2033_team15:Pea5NudeCure@localhost:{}/csc2033_team15'.format(tunnel.local_bind_port)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///temp.db'  # temporary db hosted locally to test db model while uni ssh servers are down

db = SQLAlchemy(app)


@app.route('/')
def hello_world():  # put application's code here
    return 'Hello World!'


if __name__ == '__main__':
    app.run()
