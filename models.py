from app import db

class User(db.Model):
    """Models the users table"""
    __table_name__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    role = db.Column(db.String(50))
    first_name = db.Column(db.String(50))
    last_name = db.Column(db.String(50))
    email = db.Column(db.String(50))
    phone_number = db.Column(db.String(50))
    password = db.Column(db.String(50))  # TODO: implement hashing
    long = db.Column(db.Float)
    lat = db.Column(db.Float)

    def __init__(self, role, first_name, last_name, email, phone_number, password):
        self.role = role
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.phone_number = phone_number
        self.password = password
        self.long = None  # long and lat aren't needed on signup, so are initially assigned None Types
        self.lat = None

class FoodBank(db.Model):
    """Models the foodbanks table"""
    __table_name__ = 'foodbanks'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    email = db.Column(db.String(50))
    phone_number = db.Column(db.String(50))
    long = db.Column(db.Float)
    lat = db.Column(db.Float)

    def __init__(self, name, email, phone_number, long, lat):
        self.name = name
        self.email = email
        self.phone_number = phone_number
        self.long = long
        self.lat = lat

class Items(db.Model):
    """Models the items table"""
    __table_name__ = 'items'
    sku = db.Column(db.String(10), primary_key=True)
    name = db.Column(db.String(100))
    category = db.Column(db.String(100))

    def __init__(self, sku, name, category):
        self.sku = sku
        self.name = name
        self.category = category


appointments = db.Table('appointments',
                        db.Column('appointment_id', db.String(10), primary_key=True),
                        db.Column('user_id', db.Integer, db.ForeignKey('users.id')),
                        db.Column('fb_id', db.Integer, db.ForeignKey('foodbanks.id')))

notify = db.Table('notify',
                  db.column('id', db.String(10), primary_key=True),
                  db.Column('user_id', db.Integer, db.ForeignKey('users.id')),
                  db.Column('fb_id', db.Integer, db.ForeignKey('foodbanks.id')))

stocks = db.Table('stocks',
                  db.Column('fb_id', db.Integer, db.ForeignKey('foodbanks.id'), primary_key=True),
                  db.Column('sku', db.String(10), db.ForeignKey("items.sku"), primary_key=True),
                  db.Column('quantity', db.Integer))

# note to team: I need to do more research before implementing dietReq and openingHours tables, will explain in meeting