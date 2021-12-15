from flask_login import current_user, login_user, logout_user, login_required
from flask import redirect, url_for, render_template, flash, Blueprint, session
from app import requires_roles
from admin.forms import FoodBankRegistrationForm

admin_blueprint = Blueprint('admin', __name__, template_folder='templates')

@login_required
@requires_roles('admin')
@admin_blueprint.route('/admin')
def admin():
    return render_template('admin.html')

@login_required
@requires_roles('admin')
@admin_blueprint.route('/food-bank-registration')
def food_bank_registration():
    form = FoodBankRegistrationForm()
    return render_template('food-bank-registration.html', form=form)