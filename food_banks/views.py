from flask_login import current_user, login_user, logout_user, login_required
from flask import redirect, url_for, render_template, flash, Blueprint, session, request, abort
from app import requires_roles, db
from food_banks.forms import UpdateFoodBankInformationForm, AddressForm, OpeningHoursForm
from models import Address, OpeningHours
from datetime import datetime

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
@requires_roles('food_bank')
@food_banks_blueprint.route('/update-food-bank-profile', methods=['POST', 'GET'])
def update_information():
    """Allows food bank account to update the contact information of their food bank"""
    form = UpdateFoodBankInformationForm()
    current_food_bank = current_user.associated[0]  # get food bank associated with user
    if form.validate_on_submit():  # if form is valid
        current_food_bank.update_information(name=form.name.data, email=form.email.data,
                                             phone_number=form.phone_number.data,
                                             website=form.website.data)
        return update_information()

    # get original food bank details and load them into the form
    form.name.data = current_food_bank.name
    form.email.data = current_food_bank.email
    form.phone_number.data = current_food_bank.phone_number
    form.website.data = current_food_bank.website
    return render_template('update-food-bank-profile.html', form=form)


@login_required
@requires_roles('food_bank')
@food_banks_blueprint.route('/manage-addresses')
def manage_addresses():
    """Allows food bank user account to view, add and delete previously added addresses"""
    current_food_bank = current_user.associated[0]  # get food bank associated with user
    return render_template('food-bank-manage-addresses.html', addresses=current_food_bank.address)


@login_required
@requires_roles('food_bank')
@food_banks_blueprint.route('/add-address', methods=['GET', 'POST'])
def add_address():
    """Renders the form for adding a new address"""
    form = AddressForm()
    current_food_bank = current_user.associated[0]  # get food bank associated with user
    if form.validate_on_submit():
        new_address = Address(fb_id=current_food_bank.id,
                              building_name=form.building_name.data,
                              number_and_road=form.number_and_road.data,
                              town=form.town.data,
                              postcode=form.postcode.data)

        db.session.add(new_address)
        db.session.commit()
        return manage_addresses()

    return render_template('food-bank-add-address.html', form=form)

@login_required
@requires_roles('food_bank')
@food_banks_blueprint.route('/delete-address/<address_id>', methods=['GET', 'POST'])
def delete_address(address_id):
    """Deletes a given address"""
    address = Address.query.filter_by(id=address_id).first()
    if address.fb_id != current_user.associated[0].id:  # check if current user is associated with the food bank
        abort(403)  # abort to forbidden page
    db.session.delete(address)
    db.session.commit()
    return redirect(url_for('food_banks.manage_addresses'))

@login_required
@requires_roles
@food_banks_blueprint.route('/manage-opening-hours/<address_id>', methods=['GET', 'POST'])
def manage_opening_hours(address_id):
    """Allows food bank user account to view, add and delete previously added opening hours for their food bank's
    addresses"""
    address = Address.query.filter_by(id=address_id).first()
    if address.fb_id != current_user.associated[0].id:  # check if current user is associated with the food bank
        abort(403)  # abort to forbidden page
    return render_template('food-bank-manage-hours.html', opening_hours=address.opening_hours,
                           address_id=address_id)

@login_required
@requires_roles
@food_banks_blueprint.route('/add-opening-hours/', methods=['GET', 'POST'])
def add_opening_hours():
    """Renders the form for adding new opening hours"""
    address_id = request.args.get('address_id')
    address = Address.query.filter_by(id=address_id).first()
    if address.fb_id != current_user.associated[0].id:  # check if current user is associated with the food bank
        abort(403)  # abort to forbidden page
    form = OpeningHoursForm()
    form.address_id = address_id  # set address id for the opening hours form, used in validate_unique_day
    if form.validate_on_submit():
        # concatenate the hours and minutes and convert them into a time object for storing in the database
        open_time = datetime.strptime(form.open_hour.data + ":" + form.open_minute.data, "%H:%M").time()
        close_time = datetime.strptime(form.close_hour.data + ":" + form.close_minute.data, "%H:%M").time()
        new_opening_hours = OpeningHours(address_id=address_id,
                                         day=form.day.data,
                                         open_time=open_time,
                                         close_time=close_time)
        db.session.add(new_opening_hours)
        db.session.commit()
        return redirect(url_for('food_banks.manage_opening_hours', address_id=address_id))
    return render_template('food-bank-add-opening-hours.html', form=form)

@login_required
@requires_roles('food_bank')
@food_banks_blueprint.route('/delete-opening-hours/<address_id>/<day>', methods=['GET', 'POST'])
def delete_opening_hours(address_id, day):
    """Deletes opening hours for a given address and day"""
    opening_hours = OpeningHours.query.filter_by(address_id=address_id, day=day).first()
    address = Address.query.filter_by(id=address_id).first()
    if address.fb_id != current_user.associated[0].id:  # check if current user is associated with the food bank
        abort(403)  # abort to forbidden page
    elif opening_hours:
        db.session.delete(opening_hours)
        db.session.commit()
    return redirect(url_for('food_banks.manage_opening_hours', address_id=address_id))
