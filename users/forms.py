from flask_wtf import FlaskForm, RecaptchaField
from wtforms import StringField, SubmitField, PasswordField
from wtforms.validators import Email, Length, EqualTo, ValidationError, InputRequired
from ukpostcodeutils import validation
import re


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
    if not validation.is_valid_postcode(field.data):
        raise ValidationError(f" {field.data} is not a valid postcode.")


class RegisterForm(FlaskForm):
    email = StringField(validators=[InputRequired(), Email()])
    # email is required to be filled and meet the Email requirements

    first_name = StringField(validators=[InputRequired(), character_check])
    # first name is required

    last_name = StringField(validators=[InputRequired(), character_check])
    # last name is required

    address_line_1 = StringField(validators=[InputRequired(), address_character_check])
    #

    address_line_2 = StringField(validators=[address_character_check])

    postcode = StringField(validators=[InputRequired()])

    phone_number = StringField(validators=[])

    password = PasswordField(validators=[InputRequired(), Length(min=8, max=16, message= 'Password must be between 8 and 16 '
                                                                                   'characters.')])
    # password is required to be filled, must be between 8 and 16 characters, has the option to contain a special ...
    # ... character, include at least one digit and an uppercase letter

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
    def validate_phone(self, phone_number):
        ph = re.compile(r'^(?:\s*)[0][7]\d{9}(?:\s*)$')
        if not ph.match(self.phone_number.data):
            raise ValidationError("Phone number must be 11 digits long.")


class LoginForm(FlaskForm):
    email = StringField(validators=[InputRequired(), Email()])
    password = PasswordField(validators=[InputRequired()])
    recaptcha = RecaptchaField()
    submit = SubmitField()
