from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField, FloatField
from wtforms.validators import DataRequired, Email, EqualTo, Length

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=150)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Conferma Password', validators=[DataRequired(), EqualTo('password')])
    is_farmer = BooleanField('Sono un agricoltore')
    submit = SubmitField('Registrati')

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Accedi')

class ProductForm(FlaskForm):
    name = StringField('Nome Prodotto', validators=[DataRequired()])
    description = TextAreaField('Descrizione')
    price = FloatField('Prezzo')
    submit = SubmitField('Pubblica')

class MessageForm(FlaskForm):
    content = TextAreaField('Messaggio', validators=[DataRequired()])
    submit = SubmitField('Invia')