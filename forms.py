from flask_wtf import FlaskForm
from wtforms import BooleanField, StringField, validators, SelectField, SubmitField, FloatField, PasswordField, FileField
from wtforms.validators import URL, required, NumberRange, Email
from flask_ckeditor import CKEditorField
class LocationForm(FlaskForm):
    location = SelectField('Location', choices=[('All','All'),
                                                ('Hong Kong Island', 'Hong Kong Island'),
                                                ('Kowloon', 'Kowloon'),
                                                ('New Territories', 'New Territories')])
    location_search_btn = SubmitField('Search')


class AddCafeForm(FlaskForm):
    name = StringField('Cafe Name', [required()])
    map_url = StringField('Map Url', [required()])
    img_url = FileField('Image Url', [required()])
    location_add = SelectField('Location', choices=[('Hong Kong Island', 'Hong Kong Island'),
                                                ('Kowloon', 'Kowloon'),
                                                ('New Territories', 'New Territories'),
                                                ])
    has_sockets = BooleanField('Does it have sockets?')
    has_toilet = BooleanField('Does it have Toilets?')
    has_wifi = BooleanField('Does it have Wifi?')
    can_take_calls = BooleanField('Can you take calls there?')
    seats = SelectField('Approximate number of seating', choices=[('0-10','0-10'),('10-20','10-20'),
                                                                  ('30-50','30-50')])
    coffee_price = FloatField('Approximate price of a coffee in HKD', [NumberRange(min=0, max=500)])
    opening_time = StringField('Opening Times')
    description = CKEditorField('Description')
    add_cafe_btn = SubmitField('Add Cafe')

class RegisterForm(FlaskForm):
    name = StringField('Full Name', [required()])
    email = StringField('Email Address', [required(), Email()])
    password = PasswordField('Password', [required()])
    register_submit = SubmitField('Register')

class LoginForm(FlaskForm):
    email = StringField('Email Address', [required(), Email()])
    password = PasswordField('Password', [required()])
    register_submit = SubmitField('Login')

class CommentForm(FlaskForm):
    text = CKEditorField('Comment',[required()])
    post_btn = SubmitField('Post')

class ReplyForm(FlaskForm):
    reply_text = CKEditorField('', [required()])
    reply_btn = SubmitField('Reply')