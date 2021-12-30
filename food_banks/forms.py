from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField
from wtforms.validators import Email, Length, InputRequired, ValidationError
from models import OpeningHours

# forms

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
    postcode = StringField(validators=[InputRequired(), Length(max=8)])  # TODO: Add postcode validation

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
        print(used_days)
        print(form.day.data)
        if form.day.data in used_days:
            raise ValidationError(f"Opening times for {form.day.data} have already been set.")
