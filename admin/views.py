from flask_login import current_user, login_user, logout_user, login_required
from flask import redirect, url_for, render_template, flash, Blueprint, session
from app import requires_roles, db
from admin.forms import FoodBankRegistrationForm
from models import User, FoodBank
from werkzeug.security import check_password_hash, generate_password_hash

admin_blueprint = Blueprint('admin', __name__, template_folder='templates')


@admin_blueprint.route('/admin')
@login_required
@requires_roles('admin')
def admin():
    return render_template('admin.html')


@admin_blueprint.route('/food-bank-registration', methods=['GET', 'POST'])
@login_required
@requires_roles('admin')
def food_bank_registration():
    form = FoodBankRegistrationForm()

    if form.validate_on_submit():  # check if email is already used in the database
        user = User.query.filter_by(email=form.email.data).first()

        if user:
            flash("This email is already in use")
            return render_template('food-bank-registration.html', form=form)

        new_food_bank = FoodBank(name=form.name.data,
                                 email=form.email.data,
                                 phone_number=form.phone_number.data,
                                 website=form.website.data)

        new_user = User(email=form.email.data,  # creates user to manage the food bank
                        first_name=form.name.data,
                        last_name="N/A",
                        password=generate_password_hash(form.password.data),
                        phone_number=form.phone_number.data,
                        role='food_bank')

        new_food_bank.associated.append(new_user)  # associates the user account with the food bank
        db.session.add(new_food_bank)
        db.session.add(new_user)
        db.session.commit()

    return render_template('food-bank-registration.html', form=form)
