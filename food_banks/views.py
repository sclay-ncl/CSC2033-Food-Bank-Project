from flask_login import current_user, login_user, logout_user, login_required
from flask import redirect, url_for, render_template, flash, Blueprint, session

food_banks_blueprint = Blueprint('food_banks', __name__, template_folder='templates')


@food_banks_blueprint.route('/food_banks')
def food_banks():
    return render_template('food-banks.html')