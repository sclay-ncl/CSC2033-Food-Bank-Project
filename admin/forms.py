from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, SelectField
from wtforms.validators import Email, Length, InputRequired


class FoodBankRegistrationForm(FlaskForm):
    """Form for admins to add new food banks to the database"""

    # food bank information
    name = StringField(validators=[InputRequired(), Length(max=100)])  # max length set to conform with database
    email = StringField(validators=[InputRequired(), Email(), Length(max=50)])
    phone_number = StringField(validators=[])  # TODO: Add phone validation
    website = StringField(validators=[Length(max=100)])
    password = PasswordField(validators=[InputRequired(), Length(min=8, max=16, message='Password must be between 8 '
                                                                                        'and 16 characters.')])

    # address information
    building_name = StringField(validators=[Length(max=100)])  # not all places have a building name, therefore nullable
    number_and_road = StringField(validators=[InputRequired(), Length(max=50)])
    town = StringField(validators=[InputRequired(), Length(max=50)])
    post_code = StringField(validators=[InputRequired(), Length(max=8)])  # TODO: Add postcode validation

    submit = SubmitField()

