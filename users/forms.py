import re
from flask_wtf import FlaskForm, RecaptchaField
from ukpostcodeutils import validation
from wtforms import StringField, SubmitField, PasswordField, SelectField
from wtforms.validators import Email, Length, EqualTo, ValidationError, InputRequired
from models import User


# Custom validation
def character_check(form, field):
    """
    @author: Nathan Hartley

    @returns: A message to the user that the name fields cannot contain any of the excluded characters if the
    requirements are not met
    """
    excluded_characters = "±§!@€#<$%^&*()_+={}[]:;'|<,>.?/1234567890"
    for char in field.data:
        if char in excluded_characters:
            raise ValidationError(f"Character {char} is not allowed.")


# character_check but without the numbers
def address_character_check(form, field):
    """
    @author: Nathan Hartley
    Validates that the address field does not contain any of the excluded characters
    """
    excluded_characters = "±§!@€#<#$%^&*()_+={}[]:;'|<>.?/"
    for char in field.data:
        if char in excluded_characters:
            raise ValidationError(f"Character {char} is not allowed.")


def postcode_check(form, field):
    """
    @author: Anthony Clermont
    Checks if postcode is valid
    """
    postcode = field.data.replace(" ", "")
    if not validation.is_valid_postcode(postcode.upper()):
        raise ValidationError(f" {field.data} is not a valid postcode.")


class RegisterForm(FlaskForm):
    """
    @author: Nathan Hartley
    Form for users to input their details when registering
    """
    email = StringField(validators=[InputRequired(), Email(), Length(max=50)])
    first_name = StringField(validators=[InputRequired(), character_check, Length(max=50)])
    last_name: StringField = StringField(validators=[InputRequired(), character_check, Length(max=50)])
    number_and_road = StringField(validators=[InputRequired(), address_character_check, Length(max=50)])
    town = StringField(validators=[address_character_check, Length(max=50)])
    postcode = StringField(validators=[InputRequired(), postcode_check, Length(max=50)])
    phone_number = StringField(validators=[Length(max=50)])
    role = SelectField(choices=['Picking up food', 'Donating food'])
    password = PasswordField(validators=[InputRequired(), Length(min=8, max=16, message='Password must be between 8 '
                                                                                        'and 16 characters.')])
    confirm_password = PasswordField(validators=[InputRequired(), EqualTo('password', message='This must be the same '
                                                                                              'as the password.')])
    submit = SubmitField()

    # Pattern Matching
    def validate_password(self, password):
        """
        @author: Nathan Hartley
        Validates that the password includes a digit and an uppercase

        @param: password, The password inputted by the user
        """
        p = re.compile(r'(?=.*\d)(?=.*[A-Z])')
        if not p.match(self.password.data):
            raise ValidationError("Password must contain at least 1 digit and 1 uppercase letter.")

    def validate_phone_number(self, phone_number):
        """
        @author: Nathan Hartley
        Validates that the phone number must start with 07 and be 11 digits in length

        @param: phone_number, the phone number inputted by the user
        """
        ph = re.compile(r'^(?:\s*)[0][7]\d{9}(?:\s*)$')
        if not ph.match(self.phone_number.data):
            raise ValidationError("Phone number must be 11 digits total length and start with 07.")


class LoginForm(FlaskForm):
    """
    @author: Nathan Hartley
    Form for users to input their details when logging in
    """
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
    submit = SubmitField()


class FavForm(FlaskForm):
    """
    @author: Anthony Clermont
    renders add/remove food bank as saved
    """
    add = SubmitField("Favourite")
    remove = SubmitField("Un-favourite")


class RequestResetForm(FlaskForm):
    """
    @author: Anthony Clermont
    Form for users to request a password reset
    """
    email = StringField(validators=[InputRequired(), Email(), Length(max=50)])
    submit = SubmitField('Reset Password')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is None:
            raise ValidationError('There is no account with that email. Please register an account.')


class ResetPasswordForm(FlaskForm):
    """
    @author: Anthony Clermont
    Form which allows users to enter a new password
    """
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
