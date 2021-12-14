from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, SelectField
from wtforms.validators import Email, Length, InputRequired

class OpeningTimesForm(FlaskForm):
    """Form for food banks to add opening times"""

    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    hours = ["0"+str(x) if x < 10 else str(x) for x in range(0, 25)]
    minutes = ["00", "15", "30", "45"]
    day = SelectField(choices=days, validators=[InputRequired])  # SelectField is a drop-down menu
    open_hour = SelectField(choices=hours, validators=[InputRequired])
    open_minute = SelectField(choices=minutes, validators=[InputRequired])
    close_hour = SelectField(choices=hours, validators=[InputRequired])
    close_minute = SelectField(choices=minutes, validators=[InputRequired])
