from flask_login import current_user, login_user, logout_user, login_required
from flask import redirect, url_for, render_template, flash, Blueprint, session

donate_blueprint = Blueprint('donate', __name__, template_folder='templates')


@donate_blueprint.route('/donate')
def donate():
    return render_template('donate.html')