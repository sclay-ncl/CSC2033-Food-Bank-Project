from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from functools import wraps
from flask_login import current_user, LoginManager
import socket

app = Flask(__name__)

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = \
    "mariadb+mariadbconnector://csc2033_team15:Pea5NudeCure@127.0.0.1:8989/csc2033_team15"
app.config['SECRET_KEY'] = 'LongAndRandomSecretKey'

# TODO: change these API keys, obtained from Canvas (need a URL first)
# https://www.google.com/u/2/recaptcha/admin/create
app.config['RECAPTCHA_PUBLIC_KEY'] = "6LfFdRMcAAAAAEeOwLocqoG8LhRNZhE0TYF8MdMG"
app.config['RECAPTCHA_PRIVATE_KEY'] = "6LfFdRMcAAAAAILSgmbrJcTLnkDV5fG-xwPzyoR4"

db = SQLAlchemy(app)

# FUNCTIONS
def requires_roles(*roles):
    def wrapper(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            if current_user.role not in roles:
                # Redirect the user to an unauthorised error page
                return render_template()  # TODO: add path to error page
            return f(*args, **kwargs)
        return wrapped
    return wrapper


@app.route('/')
def index():  # put application's code here
    return render_template('index.html')  # TODO: create index.html and render it (front end)


if __name__ == '__main__':
    my_host = "127.0.0.1"
    free_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    free_socket.bind((my_host, 0))
    free_socket.listen(5)
    free_port = free_socket.getsockname()[1]
    free_socket.close()

    # Login Manager
    login_manager = LoginManager()
    login_manager.login_view = 'users.login'
    login_manager.init_app(app)

    from models import User

    @login_manager.user_loader
    def load_user(id):
        return User.query.get(int(id))

    # Blueprints
    from users.views import users_blueprint
    from admin.views import admin_blueprint
    from food_banks.views import food_banks_blueprint

    app.register_blueprint(users_blueprint)
    app.register_blueprint(admin_blueprint)
    app.register_blueprint(food_banks_blueprint)

    app.run(host=my_host, port=free_port, debug=True)
