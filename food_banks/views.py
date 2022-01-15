from datetime import datetime

from flask import redirect, url_for, render_template, Blueprint, request, abort
from flask_login import current_user, login_required

from app import requires_roles, db, rss
from food_banks.forms import UpdateFoodBankInformationForm, AddressForm, OpeningHoursForm, ManualStockLevelsForm, \
    StockQuantityForm, StockManagementOptionForm
from models import Address, OpeningHours, StockLevels, Item, Stocks

food_banks_blueprint = Blueprint('food_banks', __name__, template_folder='templates')


@food_banks_blueprint.route('/update-food-bank-profile', methods=['POST', 'GET'])
@login_required
@requires_roles('food_bank')
def update_information():
    """
    @author: Sol Clay
    Allows food bank account to update the contact information of their food bank
    """
    form = UpdateFoodBankInformationForm()
    current_food_bank = current_user.associated[0]  # get food bank associated with user
    if form.validate_on_submit():  # if form is valid
        current_food_bank.update_information(name=form.name.data, email=form.email.data,
                                             phone_number=form.phone_number.data,
                                             website=form.website.data)
        return redirect(url_for("food_banks.update_information"))

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
    """
    @author: Sol Clay
    Allows food bank user account to view, add and delete previously added addresses
    """
    current_food_bank = current_user.associated[0]  # get food bank associated with user
    return render_template('food-bank-manage-addresses.html', addresses=current_food_bank.address)


@food_banks_blueprint.route('/add-address', methods=['GET', 'POST'])
@login_required
@requires_roles('food_bank')
def add_address():
    """
    @author: Sol Clay
    Renders the form for adding a new address
    """
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
    """
    @author: Sol Clay
    Deletes a given address
    """
    address = Address.query.filter_by(id=address_id).first()
    if address.fb_id != current_user.associated[0].id:  # check if current user is associated with the food bank
        abort(403)  # abort to forbidden page
    db.session.delete(address)
    db.session.commit()
    return redirect(url_for('food_banks.manage_addresses'))


@food_banks_blueprint.route('/manage-opening-hours/<address_id>', methods=['GET', 'POST'])
@login_required
@requires_roles('food_bank')
def manage_opening_hours(address_id):
    """
    @author: Sol Clay
    Allows food bank user account to view, add and delete previously added opening hours for their food bank's
    addresses
    """
    address = Address.query.filter_by(id=address_id).first()
    if address.fb_id != current_user.associated[0].id:  # check if current user is associated with the food bank
        abort(403)  # abort to forbidden page
    return render_template('food-bank-manage-hours.html', opening_hours=address.opening_hours,
                           address_id=address_id)


@food_banks_blueprint.route('/add-opening-hours/', methods=['GET', 'POST'])
@login_required
@requires_roles('food_bank')
def add_opening_hours():
    """
    @author: Sol Clay
    Renders the form for adding new opening hours
    """
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
    """
    @author: Sol Clay
    Deletes opening hours for a given address and day
    """
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
@food_banks_blueprint.route('/update-stock-option/', methods=['GET', 'POST'])
def update_stock_option():
    """
    @author: Sol Clay, Anthony Clermont
    Page to set food bank stock option preference
    """
    current_food_bank = current_user.associated[0]
    form = StockManagementOptionForm(option=current_food_bank.management_option)
    if form.validate_on_submit():
        current_food_bank.management_option = form.option.data
        db.session.commit()
    return render_template("update-stock-option.html", management_option_form=form)


@login_required
@requires_roles('food_bank')
@food_banks_blueprint.route('/manage-stock', methods=['GET', 'POST'])
def manage_stock():
    """
    @author: Anthony Clermont, Sol Clay
    Where food banks can manage their stock. Choose between stock management type: automatic or manual,
    the relevant form for the management option selected is rendered.
       """
    current_food_bank = current_user.associated[0]

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

        return render_template('manage-stock.html', form=form)

    # if food bank has chosen to automatically set stock levels
    if current_food_bank.management_option == 1:
        stock_levels = StockLevels.query.filter_by(fb_id=current_food_bank.id).first()
        items = Item.query.all()
        item_names = []
        data = {"item_forms": []}  # set up data dictionary

        for item in items:
            stock = Stocks.query.filter_by(item_id=item.id, fb_id=current_food_bank.id).first()
            item_names.append(item.name)
            item_data = {"item_id": int(item.id), "quantity": int(stock.quantity)}  # create sub-dictionary of item data
            data["item_forms"].append(item_data)
        form = StockQuantityForm(data=data)  # instantiate form

        if form.validate_on_submit():
            for item_form in form.item_forms.data:
                stock = Stocks.query.filter_by(item_id=item_form['item_id'], fb_id=current_food_bank.id).first()
                stock.quantity = item_form['quantity']

            # put data for boundary form back into database, currently not working
            categories = {'starchy', 'protein', 'fruit_veg', 'soup_sauce',
                          'drinks', 'snacks', 'condiments', 'cooking_ingredients', 'toiletries'}
            for category in categories:
                form_boundary_low = getattr(form.category_boundary_form, category+"_low")  # get data from forms
                form_boundary_high = getattr(form.category_boundary_form, category+"_high")
                setattr(stock_levels, category+"_low", form_boundary_low.data)  # set new level in database
                setattr(stock_levels, category+"_high", form_boundary_high.data)
            db.session.commit()
            current_food_bank.push_alerts()

        # set up category boundary form
        form.category_boundary_form.starchy_low.data = stock_levels.starchy_low
        form.category_boundary_form.protein_low.data = stock_levels.protein_low
        form.category_boundary_form.fruit_veg_low.data = stock_levels.fruit_veg_low
        form.category_boundary_form.soup_sauce_low.data = stock_levels.soup_sauce_low
        form.category_boundary_form.drinks_low.data = stock_levels.drinks_low
        form.category_boundary_form.snacks_low.data = stock_levels.snacks_low
        form.category_boundary_form.cooking_ingredients_low.data = stock_levels.cooking_ingredients_low
        form.category_boundary_form.condiments_low.data = stock_levels.condiments_low
        form.category_boundary_form.toiletries_low.data = stock_levels.toiletries_low
        form.category_boundary_form.starchy_high.data = stock_levels.starchy_high
        form.category_boundary_form.protein_high.data = stock_levels.protein_high
        form.category_boundary_form.fruit_veg_high.data = stock_levels.fruit_veg_high
        form.category_boundary_form.soup_sauce_high.data = stock_levels.soup_sauce_high
        form.category_boundary_form.drinks_high.data = stock_levels.drinks_high
        form.category_boundary_form.snacks_high.data = stock_levels.snacks_high
        form.category_boundary_form.cooking_ingredients_high.data = stock_levels.cooking_ingredients_high
        form.category_boundary_form.condiments_high.data = stock_levels.condiments_high
        form.category_boundary_form.toiletries_high.data = stock_levels.toiletries_high

        return render_template('manage-stock.html',
                               form=form,
                               item_names=item_names)