from datetime import datetime
from FlaskSneakers import db, login_manager
from flask_login import UserMixin
from sqlalchemy_serializer import SerializerMixin


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    image_file = db.Column(db.String(20), nullable=False, default='abobus.png')
    password = db.Column(db.String(60), nullable=False)


class Item(db.Model, SerializerMixin):
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    title = db.Column(db.String, unique=True, nullable=False)
    cost = db.Column(db.String)
    image = db.Column(db.String, unique=True, nullable=False)


class Market(db.Model, SerializerMixin):
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    username = db.Column(db.String)
    cart_items = db.Column(db.String)
    item_image = db.Column(db.String)

db.create_all()
