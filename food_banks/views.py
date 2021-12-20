from flask_login import current_user, login_user, logout_user, login_required
from flask import redirect, url_for, render_template, flash, Blueprint, session
from app import requires_roles
from food_banks.forms import UpdateFoodBankInformationForm

food_banks_blueprint = Blueprint('food_banks', __name__, template_folder='templates')

current_food_bank = current_user.assosiated[0]  # get food bank associated with user

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
@requires_roles('food_bank')
@food_banks_blueprint.route('/update-food-bank-profile', methods=['POST', 'GET'])
def update_information():
    form = UpdateFoodBankInformationForm()
    if form.validate_on_submit():  # if form is valid
        current_food_bank.update_information(name=form.name.data, email=form.email.data, phone_number=form.phone_number.data,
                                     website=form.website.data)
        return update_information()

    # get original food bank details and load them into the form
    form.name.data = current_food_bank.name
    form.email.data = current_food_bank.email
    form.phone_number.data = current_food_bank.phone_number
    form.website.data = current_food_bank.website
    return render_template('update-food-bank-profile.html', form=form)