import requests
import urllib.parse
from flask_login import current_user, login_user, logout_user, login_required
from flask import redirect, url_for, render_template, flash, Blueprint, session
from users.forms import LoginForm, RegisterForm
from app import db
from models import User
from werkzeug.security import check_password_hash

# CONFIG
users_blueprint = Blueprint('users', __name__, template_folder='templates')

""" 
Function returns the latitude and longitude of a given address
@param:address, address of desired latitude and longitude co-ordinates
@returns: tuple of latitude and longitude co-ordinates
"""
def get_lat_long(address):
    url = 'https://nominatim.openstreetmap.org/search/' + urllib.parse.quote(address) + '?format=json'
    response = requests.get(url).json()

    latitude = response[0]["lat"]
    longitude = response[0]["lon"]

    return latitude, longitude


@users_blueprint.route('/register', methods=['GET', 'POST']) # TODO: add users_blueprint (front end, requires a template/CSS)
def register():
    form = RegisterForm()

    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()

        if user:
            flash("This username already exists")
            return render_template('register.html', form=form)
        # if the inputted username matches up with a username in the db, return the user to the register page

        new_user = User(email=form.email.data, password=form.password.data) # TODO: need to pass in all parameters, also check with Sol about way to create new user, as different to last module

        db.session.add(new_user)
        db.session.commit()

        return redirect(url_for('users.login'))

    return render_template('register.html', form=form)  # TODO: create register.html (front end)


@users_blueprint.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()

    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()

        if not user or not user.password == form.password.data:
            return render_template('login.html', form=form)

        else:
            login_user(user)
            return render_template('profile.html')
    # if the login details are correct it will redirect the user to the home page
    return render_template('login.html', form=form)  # TODO: create login.html (front end)


@users_blueprint.route('/profile', methods=['GET', 'POST'])
def profile():
    return render_template('profile.html')


@login_required
@users_blueprint.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))
