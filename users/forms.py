from flask_wtf import FlaskForm, RecaptchaField
from wtforms import StringField, SubmitField, PasswordField
from wtforms.validators import DataRequired, Email, Length, EqualTo, ValidationError
from ukpostcodeutils import validation
import re


# Custom Validation
# if * or ? appears it will raise a Validation Error
def character_check(form, field):
    excluded_characters = "*?"
    for char in field.data:
        if char in excluded_characters:
            raise ValidationError(f"Character {char} is not allowed.")


def postcode_check(form, field):
    if not validation.is_valid_postcode(field.data):
        raise ValidationError(f" {field.data} is not a valid postcode.")


class RegisterForm(FlaskForm):
    email = StringField(validators=[DataRequired(), Email()])
    # email is required to be filled and meet the Email requirements

    first_name = StringField(validators=[DataRequired(), character_check])
    # first name is required

    last_name = StringField(validators=[DataRequired(), character_check])
    # last name is required

    address_line_1 = StringField(validators=[DataRequired(), character_check])
    #

    address_line_2 = StringField(validators=[character_check])

    postcode = StringField(validators=[DataRequired(), postcode_check])

    phone_number = StringField(validators=[])
    # phone number is required

    password = PasswordField(validators=[DataRequired(), Length(min=8, max=16, message= 'Password must be between 8 and 16 '
                                                                                   'characters.'), character_check])
    # password is required to be filled, must be between 8 and 16 characters, must not contain * or ?, include at...
    # ...least one digit and an uppercase letter

    confirm_password = PasswordField(validators=[DataRequired(), EqualTo('password', message='This must be the same as '
                                                                                         'the password.')])
    # confirm password must be the same as password
    submit = SubmitField()

    # Pattern Matching
    # will raise a Validation Error if password doesnt contain a digit or uppercase letter
    def validate_password(self, password):
        p = re.compile(r'(?=.*\d)(?=.*[A-Z])')
        if not p.match(self.password.data):
            raise ValidationError("Password must contain at least 1 digit and 1 uppercase letter.")

    # will raise a Validation Error if phone number isn't 11 digits in length
    def validate_phone(self, phone_number):
        ph = re.compile(r'^(?:\s*)\d{11}(?:\s*)$')
        if not ph.match(self.phone_nuumber.data):
            raise ValidationError("Phone number must be 11 digits long.")


class LoginForm(FlaskForm):
    email = StringField(validators=[DataRequired(), Email()])
    password = PasswordField(validators=[DataRequired()])
    recaptcha = RecaptchaField()
    submit = SubmitField()
