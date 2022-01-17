import logging
import socket
from functools import wraps

from flask import Flask, render_template, request, send_file
from flask_login import current_user, LoginManager, login_user
from flask_sqlalchemy import SQLAlchemy

from notifications.rss import RSSManager

app = Flask(__name__)

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///temp.db"
# app.config['SQLALCHEMY_DATABASE_URI'] = \
#     "mysql+pymysql://csc2033_team15:Pea5NudeCure@127.0.0.1:8989/csc2033_team15"
app.config['SECRET_KEY'] = '0L*[@8__9r.&s(AgSm(vZ|2=>az4|V$hoEA.TzSUex[sDy>MTo:^k!ZiEhlG'

# TODO: change these API keys, obtained from Canvas (need a URL first)
# https://www.google.com/u/2/recaptcha/admin/create
app.config['RECAPTCHA_PUBLIC_KEY'] = "6LfFdRMcAAAAAEeOwLocqoG8LhRNZhE0TYF8MdMG"
app.config['RECAPTCHA_PRIVATE_KEY'] = "6LfFdRMcAAAAAILSgmbrJcTLnkDV5fG-xwPzyoR4"

db = SQLAlchemy(app)
rss = RSSManager()


# FUNCTIONS
def requires_roles(*roles):
    """
    @author: Anthony Clermont
    wrapper function used as a decorator with other functions to check is the user can access a given page

    @param, *roles, all the roles which are required to access the webpage

    @returns, to where decorator is called
    """
    def wrapper(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            # if user is not allowed to access that page send them to page restricted error page
            if current_user.role not in roles:
                return render_template('403.html')  # TODO: add path to error page
            return f(*args, **kwargs)

        return wrapped

    return wrapper


@app.route('/')
def index():
    """
    @author: Anthony Clermont
    index page, is called when application is ran/visited

    @returns, sends the user to the home page
    """
    # increments the application visits number
    with open('admin-logs/application-visits', "r") as f:
        num = f.readline()
        num = int(num) + 1

    with open('admin-logs/application-visits', "w") as f:
        f.write(str(num))

    # testing purposes
    user = User.query.filter_by(id="2").first()
    login_user(user)

    return render_template('index.html')

@app.route("/feed")
def feed():
    return send_file("rss.xml")

# ERROR PAGE VIEWS
@app.errorhandler(400)
def bad_request(error):
    """
    @author: Anthony Clermont
    bad request error route

    @returns, sends user to error page
    """
    logging.warning('SECURITY, Error 400, Bad Request, %s, %s, %s, %s',
                    request.url,
                    request.user_agent.browser,
                    request.user_agent.platform,
                    request.environ['REMOTE_ADDR'])
    return render_template('400.html'), 400


@app.errorhandler(403)
def page_forbidden(error):
    """
    @author: Anthony Clermont
    page forbidden error route

    @returns, sends user to error page
    """
    logging.warning('SECURITY, Error 403, Page Forbidden, %s, %s, %s, %s',
                    request.url,
                    request.user_agent.browser,
                    request.user_agent.platform,
                    request.environ['REMOTE_ADDR'])
    return render_template('403.html'), 403


@app.errorhandler(404)
def page_not_found(error):
    """
    @author: Anthony Clermont
    page not found error route

    @returns, sends user to error page
    """
    logging.warning('SECURITY, Error 404, Page Not Found, %s, %s, %s, %s',
                    request.url,
                    request.user_agent.browser,
                    request.user_agent.platform,
                    request.environ['REMOTE_ADDR'])
    return render_template('404.html'), 404


@app.errorhandler(503)
def internal_error(error):
    """
    @author: Anthony Clermont
    internal error route

    @returns, sends user to error page
    """
    logging.warning('SECURITY, Error 503, Internal Service Error, %s, %s, %s, %s',
                    request.url,
                    request.user_agent.browser,
                    request.user_agent.platform,
                    request.environ['REMOTE_ADDR'])
    return render_template('503.html'), 503


if __name__ == '__main__':
    """
    @author: Anthony Clermont, Nathan Hartley
    main application run function

    @returns, runs application
    """
    # Finds free port (testing purpose)
    my_host = "127.0.0.1"
    free_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    free_socket.bind((my_host, 0))
    free_socket.listen(5)
    free_port = free_socket.getsockname()[1]
    free_socket.close()

    # Logging
    class SecurityFilter(logging.Filter):
        def filter(self, record):
            return "SECURITY" in record.getMessage()

    # Sets the logging file path and sets the format for logs to be stored
    file_handler = logging.FileHandler('admin-logs/admin-log.log', 'a')
    file_handler.setLevel(logging.WARNING)
    file_handler.addFilter(SecurityFilter())
    formatter = logging.Formatter('%(asctime)s, %(message)s', '%d/%m/%Y')
    file_handler.setFormatter(formatter)

    logger = logging.getLogger('')
    logger.propagate = False
    logger.addHandler(file_handler)

    # Login Manager
    login_manager = LoginManager()
    login_manager.login_view = 'users.login'
    login_manager.init_app(app)

    from models import User

    # Needed for flask login
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

    # Running the app
    app.run(host=my_host, port=5000, debug=True)
