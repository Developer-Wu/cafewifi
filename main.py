#!/usr/bin/python
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from forms import LocationForm, AddCafeForm, RegisterForm, LoginForm, CommentForm, ReplyForm
from flask_bootstrap import Bootstrap
from itertools import groupby
from flask_login import LoginManager, login_user, current_user, UserMixin, logout_user,login_required
from werkzeug.security import generate_password_hash, check_password_hash
from image_uploader import Uploader
from sqlalchemy.orm import relationship
from flask_gravatar import Gravatar
import datetime as dt
from comments import Comments
import requests
from flask_googlemaps import GoogleMaps, Map

# MAPS API KEY
GOOGLE_KEY = 'AIzaSyCsyXXUNMfYIOq_yIoBINLulrbU_7aGEYU'

#FLASK
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data/cafes.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'TopSecret'
app.config['GOOGLEMAPS_KEY'] = GOOGLE_KEY

GoogleMaps(app)

#FLASK LOGIN
login_manager = LoginManager()
login_manager.init_app(app)

#CONNECT TO DATABASE
db = SQLAlchemy(app)
bootstrap = Bootstrap(app)

#GRAVATAR
gravatar = Gravatar(app,
                    size=50,
                    rating='g',
                    default='retro',
                    force_default=False,
                    force_lower=False,
                    use_ssl=False,
                    base_url=None)

#Comments
comments = Comments()

############################### DATA MODELS ###########################
class Cafe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), unique=True)
    map_url = db.Column(db.String(250))
    img_url = db.Column(db.String(250))
    location = db.Column(db.String(250))
    has_sockets = db.Column(db.Boolean, default=False)
    has_toilet = db.Column(db.Boolean, default=False)
    has_wifi = db.Column(db.Boolean, default=False)
    can_take_calls = db.Column(db.Boolean, default=False)
    seats = db.Column(db.String(250), default=False)
    coffee_price = db.Column(db.String(250), default=False)
    likes = db.Column(db.Integer)
    description = db.Column(db.String(1000))
    opening_time = db.Column(db.String(60))

    post_author = relationship("User", back_populates="cafe")
    post_author_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    comment_id = relationship("Comment", back_populates="cafe")

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250))
    password = db.Column(db.String(250))
    email = db.Column(db.String(250), unique=True)

    replies = relationship("Reply", back_populates="reply_author")
    comments = relationship("Comment", back_populates="comment_author")
    cafe = relationship("Cafe", back_populates="post_author")

class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(250))
    comment_author_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    cafe = relationship("Cafe", back_populates="comment_id")
    cafe_id = db.Column(db.Integer, db.ForeignKey('cafe.id'))
    comment_author = relationship("User", back_populates="comments")
    date = db.Column(db.String(250))
    likes = db.Column(db.Integer)

    reply_id = relationship("Reply", back_populates="comment")

class Reply(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(250))
    reply_author_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    reply_author = relationship("User", back_populates="replies")
    date = db.Column(db.String(250))

    comment = relationship("Comment", back_populates="reply_id")
    comment_id = db.Column(db.Integer, db.ForeignKey('comment.id'))

db.create_all()

######################### END DATA MODELS #############################

# User Callback for Flask Login
@login_manager.user_loader
def load_user(user_id):
    return User.query.filter_by(id=user_id).first()


#HOME PAGE
@app.route('/', methods= ['GET','POST'])
def home():
    cafes = Cafe.query.all()
    location_list = [cafe.location for cafe in cafes]

    num_locations = len([location for location, _ in groupby(location_list, key=None)])
    location_search_form = LocationForm()
    add_cafe_form = AddCafeForm()
    if request.method =='POST':
        if location_search_form.validate_on_submit():
            location = location_search_form.location.data
            #Check to see if selection is All
            if location != 'All':
                return redirect(url_for('location_search', location=location))
            else:
                return redirect(url_for('all_cafes'))

    return render_template('index.html', add_cafe_form= add_cafe_form, location_search_form=location_search_form, num_locations = num_locations, cafes=cafes)


#Login
@app.route('/login', methods=['GET','POST'])
def login():
    login_form = LoginForm()
    if request.method =='POST':
        if login_form.validate_on_submit():
            email = login_form.email.data
            password = login_form.password.data
            user=User.query.filter_by(email=email).first()
            if user != None:
                if check_password_hash(pwhash=user.password,password=password):
                    login_user(user)
                    return redirect(url_for('home'))
            else:
                flash('Email does not exist')


    return render_template('login.html', login_form=login_form)

#register
@app.route('/register', methods= ["GET","POST"])
def register():
    register_form = RegisterForm()
    if request.method =='POST':
        name = register_form.name.data
        email = register_form.email.data
        password = generate_password_hash(password=register_form.password.data,
                                          method='pbkdf2:sha256',
                                          salt_length=8)
        user = User(name=name, email=email, password=password)
        db.session.add(user)
        db.session.commit()
        flash('Account created, please login!')
        return redirect('login')

    return render_template('register.html',register_form=register_form)

#Logout User
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))


# Search By location Page
@app.route('/search_by_location', methods= ['GET','POST'])
def location_search():
    # Search for all cafes by location
    location = request.args['location']
    heading = f'Cafes in {location}'

    cafes = Cafe.query.filter_by(location=location).all()

    return render_template('results.html', results= cafes, heading=heading)


# Find all Cafes
@app.route('/all_cafes', methods=['GET','POST'])
def all_cafes():
    cafes = Cafe.query.all()
    heading = 'All Cafes'
    return render_template('results.html', results=cafes, heading=heading)

# ADD A CAFE
@app.route('/add_cafe', methods=['GET','POST'])
@login_required
def add_cafe():
    add_cafe_form = AddCafeForm()
    if request.method == "POST":
        #VALIDATE FORM
        if add_cafe_form.validate_on_submit():
            img_uploader = Uploader()
            name = add_cafe_form.name.data
            map_url = add_cafe_form.map_url.data
            img_object = add_cafe_form.img_url.data
            img_uploader.upload(img_object,app)
            img_url = str(img_uploader.url)
            location = add_cafe_form.location_add.data
            has_sockets = add_cafe_form.has_sockets.data
            has_toilet = add_cafe_form.has_toilet.data
            has_wifi = add_cafe_form.has_wifi.data
            can_take_calls = add_cafe_form.can_take_calls.data
            seats = add_cafe_form.seats.data
            coffee_price = add_cafe_form.coffee_price.data
            description = add_cafe_form.description.data

            # CREATING CAFE OBJECT
            cafe = Cafe(name=name,
                        map_url=map_url,
                        img_url=img_url,
                        location=location,
                        has_sockets=has_sockets,
                        has_toilet=has_toilet,
                        has_wifi=has_wifi,
                        can_take_calls=can_take_calls,
                        seats=seats,
                        coffee_price=coffee_price,
                        post_author=current_user,
                        likes=0,
                        description=description)

            # COMMIT CHANGES TO DATABASE
            db.session.add(cafe)
            db.session.commit()

            return redirect(url_for('home'))

    return render_template('add_cafe.html', form=add_cafe_form)

# CAFE DETAILS
@app.route('/cafe_details/<cafe_id>', methods = ["GET","POST"])
def cafe_detail(cafe_id):
    cafe = Cafe.query.filter_by(id=cafe_id).first()
    comment_form = CommentForm()
    reply_form = ReplyForm()
    all_comments = Comment.query.filter_by(cafe_id=cafe_id).all()

    ###### GET LAT LONG OF
    map_params = {'query':cafe.map_url, 'country':'HK'}
    map_headers = {'Authorization':'prj_live_sk_e0fe049e370150f5a0582d14cc6ddb4028d0322e'}
    map_data = requests.get('https://api.radar.io/v1/geocode/forward', params=map_params,headers= map_headers)
    lat = map_data.json()['addresses'][0]['latitude']
    long = map_data.json()['addresses'][0]['longitude']

    # creating a map in the view
    cafe_map = Map(
        identifier="cafe",
        zoom=15,
        lat=lat,
        lng=-long,
        markers=[{'lat': lat,
                'lng': long,
                'infobox':cafe.name}]
    )

    ########## GET LAT LONG (Radar API) #########


    replies = Reply.query.all()
    if request.method == 'POST':
        if current_user.is_authenticated:
            user = User.query.filter_by(id=current_user.id).first()
            if comment_form.validate_on_submit():
                date = dt.datetime.now()
                date_string = date.strftime('%d-%m-%Y')
                text= comment_form.text.data

                comment = Comment(comment_author = user,
                                  date=date_string,
                                  cafe=cafe,
                                  text=text,
                                  likes=0)
                db.session.add(comment)
                db.session.commit()

            elif reply_form.validate_on_submit():
                comment_id = request.args.get('comment_id')
                comment = Comment.query.filter_by(id=comment_id).first()
                date = dt.datetime.now()
                date_string = date.strftime('%d-%m-%Y')
                text = reply_form.reply_text.data
                reply = Reply(reply_author=user,
                              date=date_string,
                              comment= comment,
                              text=text)
                db.session.add(reply)
                db.session.commit()
            return redirect(url_for('cafe_detail', cafe_id=cafe_id))
        else:
            flash('Not logged in')

    return render_template('cafe_details.html', cafe=cafe,
                           comment_form=comment_form,
                           comments=all_comments,
                           reply_form=reply_form,
                           replies = replies,
                           cafe_map=cafe_map)

@app.route('/like_comment/<cafe_id>/<comment_id>', methods=["GET", "POST"])
def like_comment(comment_id, cafe_id):
    comment = Comment.query.filter_by(id=int(comment_id)).first()
    comment.likes += 1
    db.session.commit()
    return redirect(url_for('cafe_detail', cafe_id=cafe_id))


if __name__ == '__main__':
    app.run(debug=True)