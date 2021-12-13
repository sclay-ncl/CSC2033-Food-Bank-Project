import requests
import urllib.parse
from flask_login import current_user, login_user, logout_user, login_required
from flask import redirect, url_for, render_template, flash, Blueprint, session
from users.forms import LoginForm, RegisterForm
from app import db, requires_roles
from models import User, FoodBank
from werkzeug.security import check_password_hash, generate_password_hash

# CONFIG
users_blueprint = Blueprint('users', __name__, template_folder='templates')


def get_lat_long(address):
    """
    Function returns the latitude and longitude of a given address

    @param: address, address of desired latitude and longitude co-ordinates
    @return: tuple of latitude and longitude co-ordinates
    """
    url = 'https://nominatim.openstreetmap.org/search/' + urllib.parse.quote(address) + '?format=json'
    response = requests.get(url).json()

    latitude = response[0]["lat"]
    longitude = response[0]["lon"]

    return latitude, longitude


@users_blueprint.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()

    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()

        if user:
            flash("This username already exists")
            return render_template('register.html', form=form)
        # if the inputted username matches up with a username in the db, return the user to the register page
        lat_long = get_lat_long(
            str(form.address_line.data) + ", " + str(form.town_city.data) + ", " + str(form.postcode.data))

        new_user = User(email=form.email.data,
                        first_name=form.first_name.data,
                        last_name=form.last_name.data,
                        password=generate_password_hash(form.password.data),
                        phone_number=form.phone_number.data,
                        role='user',  # TODO: assign different user roles (donor and collector)
                        long=lat_long[1],
                        lat=lat_long[0])

        db.session.add(new_user)
        db.session.commit()

        return redirect(url_for('users.login'))

    return render_template('register.html', form=form)


@users_blueprint.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()

    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()

        if not user or not check_password_hash(user.password, form.password.data):
            flash("incorrect username/password")
            return render_template('login.html', form=form)

        else:
            login_user(user)
            return render_template('profile.html')
    # if the login details are correct it will redirect the user to the home page
    return render_template('login.html', form=form)


@login_required
@users_blueprint.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


@login_required
@requires_roles('donor', 'collector', 'admin')
@users_blueprint.route('/profile', methods=['GET', 'POST'])
def profile():
    return render_template('profile.html',
                           acc_no=current_user.id,
                           role=current_user.role,
                           email=current_user.email,
                           firstname=current_user.first_name,
                           lastname=current_user.last_name,
                           phone=current_user.phone_number,
                           user=current_user)


@users_blueprint.route('/book_appointments')
def book_appointments():
    return render_template('book-appointments.html')


@login_required
@requires_roles('collector')
@users_blueprint.route('/edit_appointments')
def edit_appointments():
    return render_template('edit-appointments.html')


@users_blueprint.route('/food-bank-search')
def food_bank_search():
    return render_template('food-bank-search.html')


@users_blueprint.route('/food-bank-information/<food_bank_id>')
def food_bank_information(food_bank_id):
    food_bank = FoodBank.query.filter_by(id=food_bank_id).first()
    address = food_bank.address[0]
    lat_long = get_lat_long(address.number_and_road + ", " + address.town + ", " + address.post_code)
    return render_template('food-bank-information.html',
                           latitude=lat_long[0],
                           longitude=lat_long[1],
                           fb_name=food_bank.name,
                           fb_email=food_bank.email,
                           fb_phone=food_bank.phone_number,
                           fb_web=food_bank.website)


@users_blueprint.route('/donate')
def donate():
    return render_template('donate.html')
