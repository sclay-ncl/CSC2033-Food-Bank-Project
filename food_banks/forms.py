from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField, IntegerField, FieldList, FormField, Form
from wtforms.validators import Email, Length, InputRequired, ValidationError

from models import OpeningHours
from users.forms import postcode_check


class UpdateFoodBankInformationForm(FlaskForm):
    name = StringField(validators=[InputRequired(), Length(max=100)])  # max length set to conform with database
    email = StringField(validators=[InputRequired(), Email(), Length(max=50)])
    phone_number = StringField(validators=[])  # TODO: Add phone validation
    website = StringField(validators=[Length(max=100)])

    submit = SubmitField()

class AddressForm(FlaskForm):
    building_name = StringField(validators=[Length(max=100)])  # not all places have a building name, therefore nullable
    number_and_road = StringField(validators=[InputRequired(), Length(max=50)])
    town = StringField(validators=[InputRequired(), Length(max=50)])
    postcode = StringField(validators=[InputRequired(), postcode_check, Length(max=8)])

    submit = SubmitField()

class OpeningHoursForm(FlaskForm):
    """Form for food banks to add opening times"""

    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    hours = ["0" + str(x) if x < 10 else str(x) for x in range(0, 25)]
    minutes = ["00", "15", "30", "45"]
    address_id = None  # set this outside of the form before validate_on_submit
    day = SelectField(choices=days, validators=[InputRequired()])  # SelectField is a drop-down menu
    open_hour = SelectField(choices=hours, validators=[InputRequired()])
    open_minute = SelectField(choices=minutes, validators=[InputRequired()])
    close_hour = SelectField(choices=hours, validators=[InputRequired()])
    close_minute = SelectField(choices=minutes, validators=[InputRequired()])

    submit = SubmitField()

    def validate_day(form, day):
        """
        Validates that the day selected has no associated opening hours
        """
        # get days that have already had opening times set
        used_days = [x.day for x in OpeningHours.query.filter_by(address_id=form.address_id).all()]
        if form.day.data in used_days:
            raise ValidationError(f"Opening times for {form.day.data} have already been set.")

class ManualStockLevelsForm(FlaskForm):
    """ Form for food banks to manually set their stock levels """

    levels = [(2, "High"), (1, "Low"), (0, "Urgent")]
    starchy = SelectField(choices=levels, validators=[InputRequired()])
    protein = SelectField(choices=levels, validators=[InputRequired()])
    fruit_veg = SelectField(choices=levels, validators=[InputRequired()])
    soup_sauce = SelectField(choices=levels, validators=[InputRequired()])
    drinks = SelectField(choices=levels, validators=[InputRequired()])
    snacks = SelectField(choices=levels, validators=[InputRequired()])
    cooking_ingredients = SelectField(choices=levels, validators=[InputRequired()])
    condiments = SelectField(choices=levels, validators=[InputRequired()])
    toiletries = SelectField(choices=levels, validators=[InputRequired()])

    submit = SubmitField()

class ItemStockForm(Form):
    """Form for updating the quantity of an item in stock"""
    quantity = IntegerField(validators=[InputRequired()])

class CategoryBoundaryForm(Form):
    """Form for the setting of the category stock level boundaries"""
    starchy_low = IntegerField(validators=[InputRequired()])
    protein_low = IntegerField(validators=[InputRequired()])
    fruit_veg_low = IntegerField(validators=[InputRequired()])
    soup_sauce_low = IntegerField(validators=[InputRequired()])
    drinks_low = IntegerField(validators=[InputRequired()])
    snacks_low = IntegerField(validators=[InputRequired()])
    cooking_ingredients_low = IntegerField(validators=[InputRequired()])
    condiments_low = IntegerField(validators=[InputRequired()])
    toiletries_low = IntegerField(validators=[InputRequired()])

    starchy_high = IntegerField(validators=[InputRequired()])
    protein_high = IntegerField(validators=[InputRequired()])
    fruit_veg_high = IntegerField(validators=[InputRequired()])
    soup_sauce_high = IntegerField(validators=[InputRequired()])
    drinks_high = IntegerField(validators=[InputRequired()])
    snacks_high = IntegerField(validators=[InputRequired()])
    cooking_ingredients_high = IntegerField(validators=[InputRequired()])
    condiments_high = IntegerField(validators=[InputRequired()])
    toiletries_high = IntegerField(validators=[InputRequired()])

class StockQuantityForm(FlaskForm):
    """Form combing ItemStockForms used to update the quantity of stock across many items"""
    item_forms = FieldList(FormField(ItemStockForm))  # TODO see how this renders in html with front end team
    category_boundary_form = CategoryBoundaryForm()
    submit = SubmitField()

class StockManagementOptionForm(FlaskForm):
    """Form to choose between stock management options"""
    option = SelectField(choices=[(0, "Manual"), (1, "Automatic")])
    submit = SubmitField("Refresh")