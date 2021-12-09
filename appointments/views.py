from flask_login import current_user, login_user, logout_user, login_required
from flask import redirect, url_for, render_template, flash, Blueprint, session

appointments_blueprint = Blueprint('appointments', __name__, template_folder='templates')


@appointments_blueprint.route('/appointments')
def appointments():
    return render_template('appointments.html')