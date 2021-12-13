from flask_login import current_user, login_user, logout_user, login_required
from flask import redirect, url_for, render_template, flash, Blueprint, session

food_banks_blueprint = Blueprint('food_banks', __name__, template_folder='templates')


@food_banks_blueprint.route('/manage_stock')
def manage_stock():
    return render_template('manage-stock.html')

@food_banks_blueprint.route('/upcoming_appointments')
def upcoming_appointments():
    return render_template('upcoming-appointments.html')