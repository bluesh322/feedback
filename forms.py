from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField, FloatField, IntegerField, BooleanField, RadioField, SelectField
from wtforms.fields.html5 import EmailField
from wtforms.validators import Email, InputRequired, Optional, URL, NumberRange, Length
from wtforms.widgets import TextArea


class RegisterUserForm(FlaskForm):
    username = StringField("Username", validators=[InputRequired(), Length(max=20, message="Must be less than 20 characters")])
    password = PasswordField("Password", validators=[InputRequired()])
    email = EmailField("Email", validators=[InputRequired(), Email(), Length(max=50, message="Must be less than 50 characters")])
    first_name = StringField("First Name", validators=[InputRequired(), Length(max=30, message="Must be less than 30 characters")])
    last_name = StringField("Last Name", validators=[InputRequired(), Length(max=30, message="Must be less than 30 characters")])

class LoginUserForm(FlaskForm):
    username = StringField("Username", validators=[InputRequired(), Length(max=20)])
    password = PasswordField("Password", validators=[InputRequired()])

class FeedbackForm(FlaskForm):
    title = StringField("Title", validators=[InputRequired(), Length(max=100)])
    content = TextAreaField("Feedback", render_kw={'rows':10}, validators=[InputRequired()])