from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField,FloatField, IntegerField  
from wtforms.validators import  (DataRequired, Email, EqualTo, Length, ValidationError, NumberRange)

from app.models import User

class RegistrationForm(FlaskForm):
    full_name = StringField("Full Name", validators=[DataRequired(), Length(min=2, max=100)])
    email = StringField("Email", validators=[DataRequired(), Email()])
    phone_number = StringField("Phone Number", validators=[DataRequired(), Length(min=10, max=20)])
    password = PasswordField("Password", validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField("Confirm Password", validators=[DataRequired(), EqualTo("password")])
    submit = SubmitField("Register")

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError("Email is already in use. Please choose a different one.")

    def validate_phone_number(self, phone_number):
        user = User.query.filter_by(phone=phone_number.data).first()
        if user:
            raise ValidationError("Phone number is already in use. Please choose a different one.")


class LoginForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Log in")


class LoanForm(FlaskForm):
    amount = FloatField("Amount", validators=[DataRequired(), NumberRange(min=1000, max=1000000)])
    months = IntegerField("Terms (months)", validators=[DataRequired(), NumberRange(min=1, max=60)])
    purpose = StringField("Purpose", validators=[Length(max=200)])
    submit = SubmitField("Apply")