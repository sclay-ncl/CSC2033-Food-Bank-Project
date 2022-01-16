import urllib.parse
from math import cos, asin, sqrt, pi

import requests
from flask import redirect, url_for, render_template, flash, Blueprint, request, abort
from flask_login import current_user, login_user, logout_user, login_required
from werkzeug.security import check_password_hash, generate_password_hash

from app import db, requires_roles
from models import User, FoodBank, StockLevels, OpeningHours
from notifications.mail import send_reset_email
from users.forms import LoginForm, RegisterForm
from users.forms import UpdateAccountInformationForm, FavForm, RequestResetForm, ResetPasswordForm

# CONFIG
users_blueprint = Blueprint('users', __name__, template_folder='templates')


def get_lat_long(number_road, city, post_code):
    """
    @author: Anthony Clermont
    Function returns the latitude and longitude of a given address

    @param: address, address of desired latitude and longitude co-ordinates

    @return: tuple of latitude and longitude co-ordinates
    """

    def find_gap(postcode):
        # Finds where in the given postcode a space is needed
        for i in range(len(postcode)):
            if postcode[i].isdigit():
                if postcode[i + 1].isalpha() and postcode[i + 2].isalpha():
                    return postcode[0:i] + " " + postcode[i:]

    # Calls find_gap function if no gap is in the postcode
    if not " " in post_code:
        post_code = find_gap(post_code)

    address = number_road + ", " + city + ", " + post_code

    # Query open street maps to return location data
    url = 'https://nominatim.openstreetmap.org/search/' + urllib.parse.quote(address) + '?format=json'

    # Attempts to get the latitude and longitude of the given address
    try:
        response = requests.get(url).json()
        latitude = response[0]["lat"]
        longitude = response[0]["lon"]
    # Rare case of an error from open street, latitude and longitude is set to Urban Sciences Building
    except LookupError:
        latitude = "54.972572326660156"
        longitude = "-1.6141237020492554"

    return latitude, longitude

# https://stackoverflow.com/questions/4913349/haversine-formula-in-python-bearing-and-distance-between-two-gps-points
# https://stackoverflow.com/questions/41336756/find-the-closest-latitude-and-longitude
# parts of code used as reference from these links
def find_closest_fb(fb_address_lat, db_address_long):
    """
    @author: Anthony Clermont
    Function returns the latitude and longitude of the closest food bank to the logged in user.

    @param: usr_lat: The current user's latitude co-ordinate
    @param: usr_long: The current user's longitude co-ordinate
    @param: fb_lat: The food bank's latitude co-ordinate the code is currently checking
    @param: fb_long: The food bank's longitude co-ordinate the code is currently checking
    @param: fb_data: Query from the database of all food bank data
    @param: A tuple of the current user's co-ordinates

    @return: Dictionary of the co-ordinates of the closest food bank
    """

    def distance(usr_lat, usr_long, fb_lat, fb_long):
        # Converts pie to radians so can be used to calculate the distance
        radians_convert = pi / 180
        diam_earth_km = 12742  # Stores the diameter of the earth in kilometers
        d_lat = fb_lat - usr_lat  # Distance in latitude between the two points
        d_long = fb_long - usr_long  # Distance in longitude between the two points
        # Implementation of well known formula: Haversine which calculates distance between two lat, long co-ords
        haversine = 0.5 - cos(d_lat * radians_convert) / 2 + cos(usr_lat * radians_convert) * \
                    cos(fb_lat * radians_convert) * (1 - cos(d_long * radians_convert)) / 2
        dist = asin(sqrt(haversine))
        return diam_earth_km * dist

    def closest(fb_data, urs_cords):
        # Use of lambda to anonymously call distance function and then return the minimum of the values returned
        return min(fb_data, key=lambda f: distance(urs_cords["lat"], urs_cords["lon"], f["lat"], f["lon"]))

    # Stores the current users latitude and longitude in dictionary
    user_lat_long = {"lat": current_user.lat, "lon": current_user.long}
    fb_lat_long = []

    # Loops through and stores all the food bank latitude and longitudes in a dictionary and all inside an array
    for fb in range(len(fb_address_lat)):
        dict_lat_long = {"lat": float(fb_address_lat[fb]), "lon": float(db_address_long[fb])}
        fb_lat_long.append(dict_lat_long)

    return closest(fb_lat_long, user_lat_long)


@users_blueprint.route('/contact-us', methods=['GET', 'POST'])
def contact_us():
    if not current_user.is_anonymous:
        if current_user.role == 'food_bank' or current_user.role == 'admin':
            abort(403)  # abort to forbidden page

    return render_template('contact-us.html')


@users_blueprint.route('/register', methods=['GET', 'POST'])
def register():
    """
    @author: Nathan Hartley
    Function returns user to index page if they are already logged in.
    Flashes a message to the user if the email they entered is already in the database.
    Returns user to index page if all requirements have been met for the input fields.
    """
    if not current_user.is_anonymous:
        return redirect(url_for('index'))

    form = RegisterForm()

    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()

        if user:
            flash("This username already exists", 'danger')
            return render_template('register.html', form=form)
        # if the inputted username matches up with a username in the db, return the user to the register page
        lat_long = get_lat_long(str(form.number_and_road.data), str(form.town.data), str(form.postcode.data).upper())

        if form.role.data == 'Picking up food':
            usr_role = 'collector'
        else:
            usr_role = 'donor'

        new_user = User(email=form.email.data,
                        first_name=form.first_name.data,
                        last_name=form.last_name.data,
                        password=generate_password_hash(form.password.data),
                        phone_number=form.phone_number.data,
                        role=usr_role,
                        number_and_road=form.number_and_road.data,
                        town=form.town.data,
                        postcode=form.postcode.data,
                        long=lat_long[1],
                        lat=lat_long[0])

        db.session.add(new_user)
        db.session.commit()

        flash("Account Created", 'success')
        return redirect(url_for('users.login'))

    return render_template('register.html', form=form)


@users_blueprint.route('/login', methods=['GET', 'POST'])
def login():
    """
    @author: Nathan Hartley
    Function returns user to index page if they are already logged in.
    Returns user to index page after a successful login attempt.
    Flashes a message to the user if the login email or password is incorrect and cannot be found in the database.
    Returns the user to profile page after a successful login attempt if the user's role is food_bank.
    """
    if not current_user.is_anonymous:
        return redirect(url_for('index'))

    form = LoginForm()

    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()

        if not user or not check_password_hash(user.password, form.password.data):
            flash("Incorrect Username/Password", 'danger')
            return render_template('login.html', form=form)

        else:
            login_user(user)
            if user.role == 'food_bank':
                return redirect(url_for('food_banks.manage_stock'))
            else:
                return render_template('profile.html')

    return render_template('login.html', form=form)


@users_blueprint.route('/logout')
@login_required
def logout():
    """
    @author: Nathan Hartley
    Function returns user to index page and makes the user anonymous
    """
    logout_user()
    return redirect(url_for('index'))


@users_blueprint.route('/profile', methods=['GET', 'POST'])
@login_required
@requires_roles('donor', 'collector', 'admin')
def profile():
    return render_template('profile.html',
                           acc_no=current_user.id,
                           role=current_user.role,
                           email=current_user.email,
                           firstname=current_user.first_name,
                           lastname=current_user.last_name,
                           phone=current_user.phone_number,
                           user=current_user,
                           saved_fb=current_user.associated)


@users_blueprint.route('/update-profile', methods=['POST', 'GET'])
@requires_roles('donor', 'collector', 'admin')
@login_required
def update_profile():
    """
    @author: Sol Clay
    Allows the user to update their profile information
    """
    user = current_user
    form = UpdateAccountInformationForm()  # show update form
    if form.validate_on_submit():  # if form is valid
        user.update_information(first_name=form.first_name.data, last_name=form.last_name.data, email=form.email.data,
                                phone_number=form.phone_number.data, number_and_road=form.number_and_road.data,
                                town=form.town.data, postcode=form.postcode.data)
        return profile()

    # get original user details and load them into the form
    form.email.data = user.email
    form.first_name.data = user.first_name
    form.last_name.data = user.last_name
    form.number_and_road.data = user.number_and_road
    form.town.data = user.town
    form.postcode.data = user.postcode
    form.phone_number.data = user.phone_number
    form.role.data = user.role
    return render_template('update-profile.html', form=form)


@users_blueprint.route('/food-bank-search', methods=['POST', 'GET'])
def food_bank_search():
    """
    @author: Anthony Clermont
    Function loads data needed for the food bank search page and then directs the user to that page

    @return: Food bank search view for either a logged in or anonymous user
    """

    if not current_user.is_anonymous:
        if current_user.role == 'food_bank' or current_user.role == 'admin':
            abort(403)  # abort to forbidden page

    lat = []
    long = []
    fb_id_name = []
    no_dup = []

    # Loops through all food banks and if an address exists for that food bank
    # it will store the needed data in the corresponding arrays
    fb_address_data = FoodBank.query.all()
    for fb in fb_address_data:
        if len(fb.address) > 0:
            no_dup.append([fb.id, fb.name])
            for address in fb.address:
                temp_fb = [fb.id, fb.name]
                fb_id_name.append(temp_fb)
                lat.append(address.lat)
                long.append(address.long)

    # If the user is logged in the function will get additional data for the page to use:
    # Their closest food bank and all food banks the user has saved.
    if current_user.is_authenticated:
        closest_fb = find_closest_fb(lat, long)
        for fb in range(len(lat)):
            # From the co-ords of the closest food bank, loop through and find the food banks name
            if str(lat[fb]) == str(closest_fb["lat"]) and str(long[fb]) == str(closest_fb["lon"]):
                closest_fb_name_id = fb_id_name[fb][0], fb_id_name[fb][1]

        # Saving the users saved food bank id's and names
        user_info = User.query.filter_by(id=current_user.id).first()
        fav_fb_data = user_info.associated
        fav_fb = []
        for i in range(len(fav_fb_data)):
            fav_fb.append((fav_fb_data[i].id, fav_fb_data[i].name))

        return render_template('food-bank-search-logged-in.html', lat=closest_fb["lat"], long=closest_fb["lon"],
                               closest_fb=closest_fb, closest_fb_name_id=closest_fb_name_id, fav_fb=fav_fb,
                               fb_info=fb_id_name, no_dup=no_dup)

    return render_template('food-bank-search.html', lat=lat, long=long, fb_info=fb_id_name, no_dup=no_dup)


@users_blueprint.route('/food-bank-information/<food_bank_id>', methods=['POST', 'GET'])
def food_bank_information(food_bank_id):
    """
    @author: Anthony Clermont
    Function loads data needed for to display information about the chosen food bank

    @param: food_bank_id, The id of the food bank which page needs to be loaded

    @return: Food bank information view about the chosen food bank
    """

    if not current_user.is_anonymous:
        if current_user.role == 'food_bank' or current_user.role == 'admin':
            abort(403)  # abort to forbidden page

    food_bank = FoodBank.query.filter_by(id=food_bank_id).first()

    # The form used for logged in users to favourite/un-favourite the food bank
    form = FavForm()
    # if the button has been clicked
    if request.method == 'POST':
        # Checks which button has been clicked, to know whether to add/remove this food bank as a saved.
        if request.form['action'] == "add":
            current_user.associated.append(food_bank)
            db.session.commit()

        if request.form['action'] == "remove":
            current_user.associated.remove(food_bank)
            db.session.commit()

    # If food banks is saved is set to False by default
    is_fav = False
    # Will only try to change is_fav to true if user is logged in
    if current_user.is_authenticated:
        user_info = User.query.filter_by(id=current_user.id).first()
        fav_fb_data = user_info.associated

        # Loops through to see if the user has saved this food bank
        for fb in fav_fb_data:
            if str(fb.id) == str(food_bank_id):
                # If the food bank ID is found, is_fav is set to true
                is_fav = True


    # Query's data needed
    stock_levels = StockLevels.query.filter_by(fb_id=food_bank_id).first()

    fb_address_id = []
    fb_lat = []
    fb_long = []
    fb_opening_times = []
    fb_txt_address = []

    for address in food_bank.address:
        fb_txt_address.append([address.building_name, address.number_and_road, address.town, address.postcode])

        fb_lat.append(address.lat)
        fb_long.append(address.long)
        fb_address_id.append(address.id)

        opening_times = OpeningHours.query.filter_by(address_id=address.id).all()

        # loops through the data and formats it in correct way
        opening_times_data = []
        for ot in opening_times:
            opening_times_data.append([ot.day, ot.open_time, ot.close_time])

        # Dictionary of information to be passed through to HTML, default to closed
        opening_times_format = {'Monday': 'Closed',
                                'Tuesday': 'Closed',
                                'Wednesday': 'Closed',
                                'Thursday': 'Closed',
                                'Friday': 'Closed',
                                'Saturday': 'Closed',
                                'Sunday': 'Closed'}

        # loops through each opening time data and finds the corresponding day
        days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        for index in range(len(opening_times_data)):
            for day in range(len(days)):
                if days[day] == opening_times_data[index][0]:
                    # formats time correctly
                    open_t = (str(opening_times_data[index][1]))[0:5]
                    close_t = (str(opening_times_data[index][2]))[0:5]
                    # changes the dictionary data for that day
                    opening_times_format[opening_times_data[index][0]] = open_t + " - " + close_t
                    break

        fb_opening_times.append(opening_times_format)

    c_coord = [sum(fb_lat) / len(fb_lat), sum(fb_long) / len(fb_long)]

    return render_template('food-bank-information.html',
                           lat=fb_lat,
                           long=fb_long,
                           id=fb_address_id,
                           fb_stock=stock_levels,
                           fb_name=food_bank.name,
                           fb_email=food_bank.email,
                           fb_phone=food_bank.phone_number,
                           fb_web=food_bank.website,
                           fb_txt_address=fb_txt_address,
                           opening_times=fb_opening_times,
                           form=form,
                           is_fav=is_fav,
                           c_coord=c_coord)


@users_blueprint.route('/donate')
def donate():
    """
    @author: Anthony Clermont
    Function displays the donate page

    @return: Donate view
    """
    if not current_user.is_anonymous:
        if current_user.role == 'food_bank' or current_user.role == 'admin':
            abort(403)  # abort to forbidden page

    return render_template('donate.html')


@users_blueprint.route('/reset_password', methods=['GET', 'POST'])
def reset_request():
    """
    @author: Anthony Clermont
    Function loads data needed for to send password reset email

    @return: Loads either the page again if not valid or the login page
    """

    # If user is logged in they dont need to reset their password so is directed to the index page
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RequestResetForm()

    # If form is validated
    if form.validate_on_submit():
        # Get the user object
        user = User.query.filter_by(email=form.email.data).first()
        # Calls the send email function
        send_reset_email(user)
        flash('Password Email Sent', 'info')

        return redirect(url_for('users.login'))

    return render_template('reset_request.html', form=form)


@users_blueprint.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_token(token):
    """
    @author: Anthony Clermont
    Function loads data needed for to send password reset email

    @param: token, The user token used to verify the user

    @return: Loads the login page if password has been reset,
            request password reset page reset if token is invalid/expired or
            reset token page if user needs to enter a new password.
    """

    # Calls class method of the user to verify the given token, will return true if valid
    user = User.verify_reset_token(token)
    # Tells the user the code is invalid/expired and sends them to the request another reset password
    if user is None:
        flash('Invalid or Expired Token', 'warning')
        return redirect(url_for('users.reset_request'))

    # Gets the form which allows users to set a new password
    form = ResetPasswordForm()
    # If form is valid, hash the password the user has entered and store the new password in the database
    if form.validate_on_submit():
        hashed_password = generate_password_hash(form.password.data)
        user.password = hashed_password
        db.session.commit()

        flash('Password Has Been Reset', 'success')
        return redirect(url_for('users.login'))

    return render_template('reset_token.html', form=form)
