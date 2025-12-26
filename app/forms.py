from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField, FloatField, SelectField
from wtforms.validators import DataRequired, Email, EqualTo, Length, Optional
from flask_wtf.file import FileField, FileAllowed

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
    name = StringField('Nome Prodotto', validators=[DataRequired(message="Il nome del prodotto è obbligatorio")])
    description = TextAreaField('Descrizione', validators=[Optional()])
    price = FloatField('Prezzo (€)', validators=[DataRequired(message="Il prezzo è obbligatorio")])
    unit = SelectField('Unità di Misura', choices=[('kg','€/kg'), ('pezzo','€/pezzo'), ('cassetta','€/cassetta')], validators=[DataRequired()])
    image = FileField('Foto Prodotto', validators=[Optional(), FileAllowed(['jpg','jpeg','png','gif'], 'Solo immagini JPG, PNG o GIF')])
    submit = SubmitField('Pubblica Prodotto')

class MessageForm(FlaskForm):
    content = TextAreaField('Messaggio', validators=[DataRequired()])
    submit = SubmitField('Invia')

class FarmerProfileForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=150)])
    display_name = StringField('Nome Visualizzato', validators=[Optional(), Length(max=150)])
    phone = StringField('Telefono / WhatsApp', validators=[Optional(), Length(max=50)])
    company_name = StringField('Nome Azienda', validators=[DataRequired(), Length(max=200)])
    company_description = TextAreaField('Descrizione Azienda', validators=[Optional()])
    province = SelectField('Provincia', choices=[], validators=[DataRequired()])
    city = SelectField('Comune', choices=[], validators=[Optional()])
    address = StringField('Indirizzo', validators=[Optional(), Length(max=300)])
    company_logo = FileField('Logo Azienda', validators=[Optional(), FileAllowed(['jpg','jpeg','png'], 'Solo immagini')])
    company_cover = FileField('Immagine di Copertina', validators=[Optional(), FileAllowed(['jpg','jpeg','png'], 'Solo immagini')])
    delivery = BooleanField('Offri consegna')
    submit = SubmitField('Salva Profilo')

class ClientProfileForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=150)])
    display_name = StringField('Nome Visualizzato', validators=[Optional(), Length(max=150)])
    bio = TextAreaField('Descrizione', validators=[Optional()])
    address = StringField('Posizione Approssimativa', validators=[Optional(), Length(max=300)])
    profile_photo = FileField('Foto Profilo', validators=[Optional(), FileAllowed(['jpg','jpeg','png'], 'Solo immagini')])
    submit = SubmitField('Salva Profilo')