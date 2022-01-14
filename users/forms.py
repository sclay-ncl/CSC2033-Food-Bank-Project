import re

from flask_wtf import FlaskForm, RecaptchaField
from ukpostcodeutils import validation
from wtforms import StringField, SubmitField, PasswordField, SelectField
from wtforms.validators import Email, Length, EqualTo, ValidationError, InputRequired

from models import User


# Custom Validation
def character_check(form, field):
    excluded_characters = "±§!@€#<$%^&*()_+={}[]:;'|<,>.?/1234567890"
    for char in field.data:
        if char in excluded_characters:
            raise ValidationError(f"Character {char} is not allowed.")


# character_check but without the numbers
def address_character_check(form, field):
    excluded_characters = "±§!@€#<#$%^&*()_+={}[]:;'|<>.?/"
    for char in field.data:
        if char in excluded_characters:
            raise ValidationError(f"Character {char} is not allowed.")


def postcode_check(form, field):
    postcode = field.data.replace(" ", "")
    if not validation.is_valid_postcode(postcode.upper()):
        raise ValidationError(f" {field.data} is not a valid postcode.")


class RegisterForm(FlaskForm):
    email = StringField(validators=[InputRequired(), Email(), Length(max=50)])
    first_name = StringField(validators=[InputRequired(), character_check, Length(max=50)])
    last_name: StringField = StringField(validators=[InputRequired(), character_check, Length(max=50)])
    number_and_road = StringField(validators=[InputRequired(), address_character_check, Length(max=50)])
    town = StringField(validators=[address_character_check, Length(max=50)])
    postcode = StringField(validators=[InputRequired(), postcode_check, Length(max=50)])
    phone_number = StringField(validators=[Length(max=50)])
    role = SelectField(choices=['Picking up food', 'Donating food'])
    # password is required to be filled, must be between 8 and 16 characters, has the option to contain a special
    # character, include at least one digit and an uppercase letter
    password = PasswordField(validators=[InputRequired(), Length(min=8, max=16, message= 'Password must be between 8 and 16 '
                                                                                   'characters.')])
    confirm_password = PasswordField(validators=[InputRequired(), EqualTo('password', message='This must be the same as '
                                                                                         'the password.')])
    # confirm password must be the same as password
    submit = SubmitField()

    # Pattern Matching
    # will raise a Validation Error if password doesnt contain a digit or uppercase letter
    # its called implicitly because its inside of the RegisterForm class
    def validate_password(self, password):
        p = re.compile(r'(?=.*\d)(?=.*[A-Z])')
        if not p.match(self.password.data):
            raise ValidationError("Password must contain at least 1 digit and 1 uppercase letter.")

    # will raise a Validation Error if phone number isn't 11 digits in length, or start with 07
    # TODO: figure out why this isn't working, no validation for phone is working
    def validate_phone(self, phone_number):
        ph = re.compile(r'^(?:\s*)[0][7]\d{9}(?:\s*)$')
        if not ph.match(self.phone_number.data):
            raise ValidationError("Phone number must be 11 digits total length and start with 07.")


class LoginForm(FlaskForm):
    email = StringField(validators=[InputRequired(), Email()])
    password = PasswordField(validators=[InputRequired()])
    recaptcha = RecaptchaField()
    submit = SubmitField()


class UpdateAccountInformationForm(FlaskForm):
    """
    @author: Sol Clay
    Form for users to update their account information
    """
    email = StringField(validators=[InputRequired(), Email(), Length(max=50)])
    first_name = StringField(validators=[InputRequired(), character_check, Length(max=50)])
    last_name: StringField = StringField(validators=[InputRequired(), character_check, Length(max=50)])
    number_and_road = StringField(validators=[InputRequired(), address_character_check, Length(max=50)])
    town = StringField(validators=[address_character_check, Length(max=50)])
    postcode = StringField(validators=[InputRequired(), postcode_check, Length(max=50)])
    phone_number = StringField(validators=[Length(max=50)])
    role = SelectField(choices=['Picking up food', 'Donating food'])
    submit = SubmitField()


class FavForm(FlaskForm):
    add = SubmitField("Favourite")
    remove = SubmitField("Un-favourite")


class RequestResetForm(FlaskForm):
    email = StringField(validators=[InputRequired(), Email(), Length(max=50)])
    submit = SubmitField('Reset Password')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is None:
            raise ValidationError('There is no account with that email. Please register an account.')


class ResetPasswordForm(FlaskForm):
    password = PasswordField(
        validators=[InputRequired(), Length(min=8, max=16, message='Password must be between 8 and 16 '
                                                                   'characters.')])
    confirm_password = PasswordField(
        validators=[InputRequired(), EqualTo('password', message='This must be the same as '
                                                                 'the password.')])
    submit = SubmitField('Reset Password')

    def validate_password(self, password):
        p = re.compile(r'(?=.*\d)(?=.*[A-Z])')
        if not p.match(self.password.data):
            raise ValidationError("Password must contain at least 1 digit and 1 uppercase letter.")




