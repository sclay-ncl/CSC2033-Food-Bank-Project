from app import db
from flask_login import UserMixin


class User(db.Model, UserMixin):
    """Models the user table:
    Stores all user information"""

    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    role = db.Column(db.String(50), nullable=False)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(50), nullable=False)
    phone_number = db.Column(db.String(50), nullable=False)
    password = db.Column(db.String(50), nullable=False)  # TODO: implement hashing
    long = db.Column(db.Float)
    lat = db.Column(db.Float)

    diet_req = db.relationship('DietReq')


class FoodBank(db.Model):
    """Models the food_bank table:
    Stores all Food Bank information"""

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(50), nullable=False)
    phone_number = db.Column(db.String(50), nullable=False)
    website = db.Column(db.String(100))

    address = db.relationship('Address')
    stock_levels = db.relationship('StockLevels')


class Item(db.Model):
    """Models the item table:
    Stores item information"""

    id = db.Column(db.String(10), primary_key=True)  # SKU stands for Stock Keeping Unit
    name = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(100), nullable=False)


class OpeningHours(db.Model):
    """Models opening_hours table:
    Stores the opening and closing times for a given day of a food bank address"""

    address_id = db.Column(db.Integer, db.ForeignKey('address.id'), primary_key=True)
    day = db.Column(db.String(8), primary_key=True)
    open_time = db.Column(db.Time, nullable=False)
    close_time = db.Column(db.Time, nullable=False)


class Address(db.Model):
    """Models address table:
    Store the address of a food bank"""

    id = db.Column(db.Integer, primary_key=True)
    fb_id = db.Column(db.Integer, db.ForeignKey('food_bank.id'))
    building_name = db.Column(db.String(100))
    number_and_road = db.Column(db.String(50), nullable=False)
    town = db.Column(db.String(50), nullable=False)
    post_code = db.Column(db.String(7), nullable=False)

    opening_hours = db.relationship('OpeningHours')

class DietReq(db.Model):
    """Models the diet_req table:
    Stores a user's dietary requirements note"""

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    note = db.Column(db.String(500), nullable=False)


class StockLevels(db.Model):
    """Models the stock_levels table:
    Stores information about the stock level of each category of item for each food bank
    2 is high stock, 1 is low stock, 0 is urgent
    Also stores the bounds for stock level rankings"""

    fb_id = db.Column(db.Integer, db.ForeignKey('food_bank.id'), primary_key=True)
    # stock levels
    starchy = db.Column(db.Integer)
    protein = db.Column(db.Integer)
    fruit_veg = db.Column(db.Integer)
    soup_sauce = db.Column(db.Integer)
    drinks = db.Column(db.Integer)
    snacks = db.Column(db.Integer)
    cooking_ingredients = db.Column(db.Integer)
    condiments = db.Column(db.Integer)
    toiletries = db.Column(db.Integer)
    # stock level high stock bounds
    starchy_high = db.Column(db.Integer)
    protein_high = db.Column(db.Integer)
    fruit_veg_high = db.Column(db.Integer)
    soup_sauce_high = db.Column(db.Integer)
    drinks_high = db.Column(db.Integer)
    snacks_high = db.Column(db.Integer)
    cooking_ingredients_high = db.Column(db.Integer)
    condiments_high = db.Column(db.Integer)
    toiletries_high = db.Column(db.Integer)
    # stock level low stock bounds
    starchy_low = db.Column(db.Integer)
    protein_low = db.Column(db.Integer)
    fruit_veg_low = db.Column(db.Integer)
    soup_sauce_low = db.Column(db.Integer)
    drinks_low = db.Column(db.Integer)
    snacks_low = db.Column(db.Integer)
    cooking_ingredients_low = db.Column(db.Integer)
    condiments_low = db.Column(db.Integer)
    toiletries_low = db.Column(db.Integer)


appointments = db.Table('appointments',
                        db.Column('appointment_id', db.String(10), primary_key=True),
                        db.Column('user_id', db.Integer, db.ForeignKey('user.id'), nullable=False),
                        db.Column('fb_id', db.Integer, db.ForeignKey('food_bank.id'), nullable=False),
                        db.Column('datetime', db.DateTime, nullable=False))

notify = db.Table('notify',
                  db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
                  db.Column('fb_id', db.Integer, db.ForeignKey('food_bank.id'), primary_key=True))

stocks = db.Table('stocks',
                  db.Column('fb_id', db.Integer, db.ForeignKey('food_bank.id'), primary_key=True),
                  db.Column('item_id', db.String(10), db.ForeignKey("item.id"), primary_key=True),
                  db.Column('quantity', db.Integer, nullable=False))


def init_db():
    db.drop_all()
    db.create_all()
    user = User(role='admin',
                first_name='John',
                last_name='Doe',
                email='johndoe@email.com',
                phone_number='123456789',
                password='IloveSecurity')
    db.session.add(user)
    db.session.commit()