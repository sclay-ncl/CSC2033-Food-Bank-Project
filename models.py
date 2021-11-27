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

appointments = db.Table('appointments',
                        db.Column('appointment_id', db.String(10), primary_key=True),
                        db.Column('user_id', db.Integer, db.ForeignKey('users.id')),
                        db.Column('fb_id'), db.Integer, db.ForeignKey('foodbanks.id'))

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



def init_db():
    db.drop_all()
    db.create_all()
    admin = User(email='admin@email.com')
    db.session.add(admin)
    db.session.commit()
