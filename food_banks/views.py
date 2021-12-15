from flask_login import current_user, login_user, logout_user, login_required
from flask import redirect, url_for, render_template, flash, Blueprint, session
from app import requires_roles
from food_banks.forms import UpdateFoodBankInformationForm

food_banks_blueprint = Blueprint('food_banks', __name__, template_folder='templates')

@login_required
@requires_roles('food_bank')
@food_banks_blueprint.route('/manage-stock')
def manage_stock():
    return render_template('manage-stock.html')

@login_required
@requires_roles('food_bank')
@food_banks_blueprint.route('/upcoming-appointments')
def upcoming_appointments():
    return render_template('upcoming-appointments.html')

@login_required
@food_banks_blueprint.route('/update-food-bank-profile')
def update_information():
    form = UpdateFoodBankInformationForm()
    # TODO: actually use form data
    return render_template('update-food-bank-profile.html', form=form)