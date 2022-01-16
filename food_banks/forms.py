import re
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField, IntegerField, FieldList, FormField, Form
from wtforms.validators import Email, Length, InputRequired, ValidationError

from models import OpeningHours
from users.forms import postcode_check


class UpdateFoodBankInformationForm(FlaskForm):
    """
    @author: Sol Clay
    Form for food banks to update their displayed infomration
    """
    name = StringField(validators=[InputRequired(), Length(max=100)])  # max length set to conform with database
    email = StringField(validators=[InputRequired(), Email(), Length(max=50)])
    phone_number = StringField(validators=[Length(max=50)])
    website = StringField(validators=[Length(max=100)])

    def validate_phone_number(self, phone_number):
        """
        @author: Nathan Hartley
        @param: phone_number - The phone number inputted by the user

        @returns: A message to the user that the phone number must start with 07 and be 11 digits in length if it
        does not meet the requirements
        """
        ph = re.compile(r'^(?:\s*)[0][7]\d{9}(?:\s*)$')
        if not ph.match(self.phone_number.data):
            raise ValidationError("Phone number must be 11 digits total length and start with 07.")

    submit = SubmitField()


class AddressForm(FlaskForm):
    """
    @author: Sol Clay
    Form for food banks to add an address to their information page
    """
    building_name = StringField(validators=[Length(max=100)])  # not all places have a building name, therefore nullable
    number_and_road = StringField(validators=[InputRequired(), Length(max=50)])
    town = StringField(validators=[InputRequired(), Length(max=50)])
    postcode = StringField(validators=[InputRequired(), postcode_check, Length(max=8)])

    submit = SubmitField()


class OpeningHoursForm(FlaskForm):
    """
    @author: Sol Clay
    Form for food banks to add opening times to an address
    """

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
        @author: Sol Clay
        Validates that the day selected has no associated opening hours
        """
        # get days that have already had opening times set
        used_days = [x.day for x in OpeningHours.query.filter_by(address_id=form.address_id).all()]
        if form.day.data in used_days:
            raise ValidationError(f"Opening times for {form.day.data} have already been set.")


class ManualStockLevelsForm(FlaskForm):
    """
    @author: Sol Clay
    Form for food banks to manually set their stock levels
    """

    levels = [(2, "High"), (1, "Low"), (0, "Urgent")]
    starchy = SelectField(choices=levels)
    protein = SelectField(choices=levels)
    fruit_veg = SelectField(choices=levels)
    soup_sauce = SelectField(choices=levels)
    drinks = SelectField(choices=levels)
    snacks = SelectField(choices=levels)
    cooking_ingredients = SelectField(choices=levels)
    condiments = SelectField(choices=levels)
    toiletries = SelectField(choices=levels)

    submit = SubmitField()


class ItemStockForm(Form):
    """
    @author: Sol Clay
    Form for updating the quantity of an item in stock
    """
    item_id = IntegerField()  # not rendered, used to store item_id as formfield destroys non-field variables#
    quantity = IntegerField()


class CategoryBoundaryForm(Form):
    """
    @author: Sol Clay
    Form for the setting of the category stock level boundaries
    """
    starchy_low = IntegerField()
    protein_low = IntegerField()
    fruit_veg_low = IntegerField()
    soup_sauce_low = IntegerField()
    drinks_low = IntegerField()
    snacks_low = IntegerField()
    cooking_ingredients_low = IntegerField()
    condiments_low = IntegerField()
    toiletries_low = IntegerField()

    starchy_high = IntegerField()
    protein_high = IntegerField()
    fruit_veg_high = IntegerField()
    soup_sauce_high = IntegerField()
    drinks_high = IntegerField()
    snacks_high = IntegerField()
    cooking_ingredients_high = IntegerField()
    condiments_high = IntegerField()
    toiletries_high = IntegerField()


class StockQuantityForm(FlaskForm):
    """
    @author: Sol Clay
    Form combining ItemStockForms and CategoryBoundaryForm used to update the quantity of stock across many items
    """
    item_forms = FieldList(FormField(ItemStockForm))
    category_boundary_form = FormField(CategoryBoundaryForm)
    submit = SubmitField()


class StockManagementOptionForm(FlaskForm):
    """
    @author: Sol Clay
    Form to choose between stock management options
    """
    option = SelectField(choices=[(0, "Manual"), (1, "Automatic")])
    submit = SubmitField()
