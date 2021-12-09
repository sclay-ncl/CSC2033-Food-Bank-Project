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
    notify = db.relationship('FoodBank',
                             secondary='notify',
                             backref=db.backref('notify', lazy='dynamic'))


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

    def update_stock_levels(self):
        """
        Calculates and sets the stock levels for the food bank based on the quantity of items in each category
        """
        stock_levels = StockLevels.query.filter_by(fb_id=self.id).first()  # get stock_level table for this food bank
        categories = {'starchy', 'protein', 'fruit_veg', 'soup_sauce',
                      'drinks', 'snacks', 'condiments', 'cooking_ingredients', 'toiletries'}
        for category in categories:
            # get the ids of all the items stocked in given category
            # the list comprehension extracts the integer from the returned tuple
            item_ids = [x[0] for x in Item.query.filter_by(category=category).with_entities(Item.id).all()]
            total_quantity = 0
            for item_id in item_ids:
                # go through each item and sum their quantities
                total_quantity += \
                    Stocks.query.filter_by(fb_id=self.id, item_id=item_id).with_entities(Stocks.quantity).first()[0]
            low_boundary = getattr(stock_levels, category+"_low")  # get the boundaries for the category
            high_boundary = getattr(stock_levels, category+"_high")
            if total_quantity < low_boundary:  # decide stock level based on total quantity
                level = 0
            elif total_quantity < high_boundary:
                level = 1
            else:
                level = 2
            setattr(stock_levels, category, level)  # set the stock level
            db.session.commit()

class Item(db.Model):
    """Models the item table:
    Stores item information"""

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(100), nullable=False)


class OpeningHours(db.Model):
    """Models opening_hours table:
    Stores the opening and closing times for a given day of a food bank address"""

    address_id = db.Column(db.Integer, db.ForeignKey('address.id'), primary_key=True)
    day = db.Column(db.String(8), primary_key=True)
    open_time = db.Column(db.String(5), nullable=False)
    close_time = db.Column(db.String(5), nullable=False)


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
    starchy_high = db.Column(db.Integer, default=100)
    protein_high = db.Column(db.Integer, default=100)
    fruit_veg_high = db.Column(db.Integer, default=100)
    soup_sauce_high = db.Column(db.Integer, default=100)
    drinks_high = db.Column(db.Integer, default=100)
    snacks_high = db.Column(db.Integer, default=100)
    cooking_ingredients_high = db.Column(db.Integer, default=100)
    condiments_high = db.Column(db.Integer, default=100)
    toiletries_high = db.Column(db.Integer, default=100)
    # stock level low stock bounds
    starchy_low = db.Column(db.Integer, default=10)
    protein_low = db.Column(db.Integer, default=10)
    fruit_veg_low = db.Column(db.Integer, default=10)
    soup_sauce_low = db.Column(db.Integer, default=10)
    drinks_low = db.Column(db.Integer, default=10)
    snacks_low = db.Column(db.Integer, default=10)
    cooking_ingredients_low = db.Column(db.Integer, default=10)
    condiments_low = db.Column(db.Integer, default=10)
    toiletries_low = db.Column(db.Integer, default=10)


class Appointment(db.Model):
    """Models the appointment association table that associates
     the food_bank and user tables"""
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    fb_id = db.Column(db.Integer, db.ForeignKey('food_bank.id'), primary_key=True)
    datetime = db.Column(db.DateTime, primary_key=True)

    user = db.relationship('User', backref=db.backref('appointments'))
    food_bank = db.relationship('FoodBank', backref=db.backref('appointments'))


class Stocks(db.Model):
    """Models the stocks association table that associates
     the food_bank and item tables"""
    fb_id = db.Column(db.Integer, db.ForeignKey('food_bank.id'), primary_key=True)
    item_id = db.Column(db.Integer, db.ForeignKey("item.id"), primary_key=True)
    quantity = db.Column(db.Integer, nullable=False)

    food_bank = db.relationship('FoodBank', backref=db.backref('items'))
    item = db.relationship('Item', backref=db.backref('stocked_at'))


notify = db.Table('notify',
                  db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
                  db.Column('fb_id', db.Integer, db.ForeignKey('food_bank.id'), primary_key=True))


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
