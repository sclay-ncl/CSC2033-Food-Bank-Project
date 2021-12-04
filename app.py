from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from functools import wraps
from flask_login import current_user, LoginManager

app = Flask(__name__)

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = \
    "mariadb+mariadbconnector://csc2033_team15:Pea5NudeCure@127.0.0.1:8989/csc2033_team15"

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

    # Login Manager
    login_manager = LoginManager()
    login_manager.login_view = 'users.login'
    login_manager.init_app(app)

    from models import User

    @login_manager.user_loader
    def load_user(id):
        return User.query.get(int(id))

    # Blueprints
    from users.views import users_blueprint  # TODO: add users_blueprint to users.views
    app.register_blueprint(users_blueprint)

    app.run()
