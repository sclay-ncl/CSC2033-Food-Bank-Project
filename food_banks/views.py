from flask_login import current_user, login_required
from flask import redirect, url_for, render_template, flash, Blueprint, session, request, abort
from app import requires_roles, db
from food_banks.forms import UpdateFoodBankInformationForm, AddressForm, OpeningHoursForm, ManualStockLevelsForm, StockQuantityForm, ItemStockForm, StockManagementOptionForm
from models import Address, OpeningHours, StockLevels, Item, Stocks
from datetime import datetime
from wtforms import FormField

food_banks_blueprint = Blueprint('food_banks', __name__, template_folder='templates')


@food_banks_blueprint.route('/update-food-bank-profile', methods=['POST', 'GET'])
@login_required
@requires_roles('food_bank')
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


@food_banks_blueprint.route('/manage-addresses')
@login_required
@requires_roles('food_bank')
def manage_addresses():
    """Allows food bank user account to view, add and delete previously added addresses"""
    current_food_bank = current_user.associated[0]  # get food bank associated with user
    return render_template('food-bank-manage-addresses.html', addresses=current_food_bank.address)


@food_banks_blueprint.route('/add-address', methods=['GET', 'POST'])
@login_required
@requires_roles('food_bank')
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


@food_banks_blueprint.route('/delete-address/<address_id>', methods=['GET', 'POST'])
@login_required
@requires_roles('food_bank')
def delete_address(address_id):
    """Deletes a given address"""
    address = Address.query.filter_by(id=address_id).first()
    if address.fb_id != current_user.associated[0].id:  # check if current user is associated with the food bank
        abort(403)  # abort to forbidden page
    db.session.delete(address)
    db.session.commit()
    return redirect(url_for('food_banks.manage_addresses'))


@food_banks_blueprint.route('/manage-opening-hours/<address_id>', methods=['GET', 'POST'])
@login_required
def manage_opening_hours(address_id):
    """Allows food bank user account to view, add and delete previously added opening hours for their food bank's
    addresses"""
    address = Address.query.filter_by(id=address_id).first()
    if address.fb_id != current_user.associated[0].id:  # check if current user is associated with the food bank
        abort(403)  # abort to forbidden page
    return render_template('food-bank-manage-hours.html', opening_hours=address.opening_hours,
                           address_id=address_id)


@food_banks_blueprint.route('/add-opening-hours/', methods=['GET', 'POST'])
@login_required
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
                                         day=form.day.data.capitalize(),
                                         open_time=open_time,
                                         close_time=close_time)
        db.session.add(new_opening_hours)
        db.session.commit()
        return redirect(url_for('food_banks.manage_opening_hours', address_id=address_id))
    return render_template('food-bank-add-opening-hours.html', form=form)


@food_banks_blueprint.route('/delete-opening-hours/<address_id>/<day>', methods=['GET', 'POST'])
@login_required
@requires_roles('food_bank')
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


@login_required
@requires_roles('food_bank')
@food_banks_blueprint.route('/manage-stock', methods=['GET', 'POST'])
def manage_stock():
    """Where food banks can manage their stock. Choose between stock management type: automatic or manual,
    the relevant form for the management option selected is rendered.
       """
    current_food_bank = current_user.associated[0]
    management_option_form = StockManagementOptionForm(option=current_food_bank.management_option)
    if management_option_form.validate_on_submit():
        current_food_bank.management_option = management_option_form.option.data
        db.session.commit()

    # if food bank has chosen to manually set stock levels
    if current_food_bank.management_option == 0:
        stock_levels = StockLevels.query.filter_by(fb_id=current_food_bank.id).first()
        form = ManualStockLevelsForm(starchy=stock_levels.starchy,  # sets levels from database
                                     protein=stock_levels.protein,
                                     fruit_veg=stock_levels.fruit_veg,
                                     soup_sauce=stock_levels.soup_sauce,
                                     drinks=stock_levels.drinks,
                                     snacks=stock_levels.snacks,
                                     cooking_ingredients=stock_levels.cooking_ingredients,
                                     condiments=stock_levels.condiments,
                                     toiletries=stock_levels.toiletries)
        if form.validate_on_submit():
            stock_levels.starchy = form.starchy.data
            stock_levels.protein = form.protein.data
            stock_levels.fruit_veg = form.fruit_veg.data
            stock_levels.soup_sauce = form.soup_sauce.data
            stock_levels.drinks = form.drinks.data
            stock_levels.snacks = form.snacks.data
            stock_levels.cooking_ingredients = form.cooking_ingredients.data
            stock_levels.condiments = form.condiments.data
            stock_levels.toiletries = form.toiletries.data
            db.session.commit()

        return render_template('manage-stock.html', management_option_form=management_option_form, form=form)

    # if food bank has chosen to automatically set stock levels
    if current_food_bank.management_option == 1:
        items = Item.query.all()
        form = StockQuantityForm()
        item_dict = {}  # stores item_form and stock object as a key,value pair
        item_names = []  # stores item names to pass to html
        for item in items:
            stock = Stocks.query.filter_by(fb_id=current_food_bank.id, item_id=item.id).first()
            item_form = ItemStockForm()
            item_dict[item_form] = stock
            item_names.append(item.name)
            item_form.quantity = stock.quantity
            form.item_forms.append_entry(item_form)
        if form.validate_on_submit():
            for item_form in form.item_forms:
                stock = item_dict[item_form]  # fetch correct stock for form
                stock.quantity = item_form.quantity.data
                db.session.commit()

        return render_template('manage-stock.html', management_option_form=management_option_form, form=form, item_names=item_names)

