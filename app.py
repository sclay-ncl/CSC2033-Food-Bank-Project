from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
import socket

app = Flask(__name__)


app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# app.config['SQLALCHEMY_DATABASE_URI'] = \
#     'mysql+pymysql:///csc2033_team15:Pea5NudeCure@localhost:{}/csc2033_team15'.format(tunnel.local_bind_port)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///temp.db'  # temporary db hosted locally to test db model while uni ssh servers are down

db = SQLAlchemy(app)


@app.route('/')
def index():  # put application's code here
    return render_template('index.html')


if __name__ == '__main__':
    from users.views import users_blueprint  # TODO: add users_blueprint to users.views

    app.register_blueprint(users_blueprint)

    my_host = "127.0.0.1"
    free_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    free_socket.bind((my_host, 0))
    free_socket.listen(5)
    free_port = free_socket.getsockname()[1]
    free_socket.close()

    app.run(host=my_host, port=free_port, debug=True)
