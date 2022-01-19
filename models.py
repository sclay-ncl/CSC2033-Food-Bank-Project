from flask_login import UserMixin
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer

from app import db, rss, app
from notifications.mail import send_mail

class User(db.Model, UserMixin):
    """
    @author: Sol Clay
    Models the user table:
    Stores all user information
    """

    id = db.Column(db.Integer, primary_key=True)
    role = db.Column(db.String(50), nullable=False)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(50), nullable=False)
    phone_number = db.Column(db.String(50), nullable=False)
    password = db.Column(db.String(255), nullable=False)
    number_and_road = db.Column(db.String(50))
    town = db.Column(db.String(50))
    postcode = db.Column(db.String(8))
    long = db.Column(db.Float)
    lat = db.Column(db.Float)

    associated = db.relationship('FoodBank',
                                 secondary='associate',
                                 backref=db.backref('associated', lazy='dynamic'))

    def update_information(self, first_name, last_name, email, phone_number, number_and_road, town, postcode):
        """
        @author: Sol Clay
        Updates information about the User

        @param: first_name, The user's first name
        @param: last_name, The user's last name
        @param: email, The user's email
        @param: phone_number, The user's phone number
        @param: number_and_rood, The user's house number and road
        @param: town, The user's town/city
        @param: postcode, The user's postcode
        """
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.phone_number = phone_number
        self.number_and_road = number_and_road
        self.town = town
        self.postcode = postcode
        db.session.commit()

    def get_reset_token(self, expires_sec=900):
        """
            @author: Anthony Clermont
            Generates the users reset token

            @param: expires_sec, the amount of time the token will be valid: 15 minutes

            @return: token needed to reset user's password
        """
        s = Serializer(app.config['SECRET_KEY'], expires_sec)
        return s.dumps({'user_id': self.id}).decode('utf-8')

    @staticmethod
    def verify_reset_token(token):
        """
            @author: Anthony Clermont
            Checks if the token given is valid

            @param: token, the token given by the user which needs to be authenticated

            @return: None if token is invalid or the user object if true
        """
        s = Serializer(app.config['SECRET_KEY'])
        try:
            user_id = s.loads(token)['user_id']
        except:
            return None
        return User.query.get(user_id)


class FoodBank(db.Model):
    """
    @author: Sol Clay
    Models the food_bank table:
    Stores all Food Bank information
    """

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(50), nullable=False)
    phone_number = db.Column(db.String(50), nullable=False)
    website = db.Column(db.String(100))
    management_option = db.Column(db.Integer, default=0, nullable=False)
    # stores how the food bank want to manage their stock, 0 is manual - 1 is automatic

    address = db.relationship('Address', cascade="delete, delete-orphan")
    stock_levels = db.relationship('StockLevels', cascade="delete, delete-orphan")

    def update_information(self, name, email, phone_number, website):
        """
        @author: Sol Clay
        Updates information about the Food Bank

        @param: name, The food bank's name
        @param: email, The food bank's contact email
        @param: phone_number, The food bank's contact phone number
        @param: website, The food bank's website
        """
        self.name = name
        self.email = email
        self.phone_number = phone_number
        self.website = website
        db.session.commit()

    def update_stock_levels(self):
        """
        @author: Sol Clay
        Calculates and sets the stock levels for the food bank based on the quantity of items in each category

        @return urgent_categories: list of categories that have urgent level of stock
        """
        stock_levels = StockLevels.query.filter_by(fb_id=self.id).first()  # get stock_level table for this food bank
        categories = ['starchy', 'protein', 'fruit_veg', 'soup_sauce',
                      'drinks', 'snacks', 'condiments', 'cooking_ingredients', 'toiletries']
        urgent_categories = []
        for category in categories:
            # get the ids of all the items stocked in given category
            # the list comprehension extracts the integer from the returned tuple
            item_ids = [x[0] for x in Item.query.filter_by(category=category).with_entities(Item.id).all()]
            total_quantity = 0
            for item_id in item_ids:
                # go through each item and sum their quantities
                total_quantity += \
                    Stocks.query.filter_by(fb_id=self.id, item_id=item_id).with_entities(Stocks.quantity).first()[0]
            low_boundary = getattr(stock_levels, category + "_low")  # get the boundaries for the category
            high_boundary = getattr(stock_levels, category + "_high")
            if total_quantity < low_boundary:  # decide stock level based on total quantity
                level = 0
                urgent_categories.append(category)
            elif total_quantity < high_boundary:
                level = 1
            else:
                level = 2
            setattr(stock_levels, category, level)  # set the stock level
        db.session.commit()
        return urgent_categories

    def generate_alert(self, urgent_categories):
        """
        @author: Sol Clay

        Generates a text string used for notifying donors about the categories in which stock in urgent

        @param urgent_categories: list of categories that have an urgent level of stock
        @return message: formatted text string including the name of the food bank, all urgent categories and a link to
        donation suggestions.
        """
        category_key = {"fruit_veg": "Fruit and vegetables",
                        "soup_sauce": "Soups and sauces",
                        "cooking_ingredients": "Cooking ingredients",
                        "starchy": "Starchy foods",
                        "protein": "Protein rich foods"}
        readable_categories = [category_key[c] if c in category_key.keys()
                               else c.capitalize() for c in urgent_categories]
        categories_string = "\n- ".join(readable_categories)
        examples_url = "https://www.trusselltrust.org/get-help/emergency-food/food-parcel/"
        message = f"{self.name} has urgently low stock in the following categories:\n" \
                  f"- {categories_string}\n" \
                  f"For examples of what to donate for each category, please visit {examples_url}"
        return message

    def push_alerts(self, urgent_categories):
        """
        @author: Sol Clay

        Pushes alerts to donor users and the rss feed
        """
        if len(urgent_categories) > 0:
            generated_message = self.generate_alert(urgent_categories)
            rss.generate_item(food_bank_id=self.id, generated_message=generated_message)
            rss.write_feed()
            send_mail(self.id, msg=generated_message)


class Item(db.Model):
    """
    @author: Sol Clay

    Models the item table:
    Stores item information
    """

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(100), nullable=False)


class OpeningHours(db.Model):
    """
    @author: Sol Clay

    Models opening_hours table:
    Stores the opening and closing times for a given day of a food bank address
    """

    address_id = db.Column(db.Integer, db.ForeignKey('address.id'), primary_key=True)
    day = db.Column(db.String(9), primary_key=True)
    open_time = db.Column(db.Time, nullable=False)
    close_time = db.Column(db.Time, nullable=False)


class Address(db.Model):
    """
    @author: Sol Clay

    Models address table:
    Store the address of a food bank
    """

    id = db.Column(db.Integer, primary_key=True)
    fb_id = db.Column(db.Integer, db.ForeignKey('food_bank.id'))
    building_name = db.Column(db.String(100))
    number_and_road = db.Column(db.String(50), nullable=False)
    town = db.Column(db.String(50), nullable=False)
    postcode = db.Column(db.String(8), nullable=False)
    lat = db.Column(db.Float)
    long = db.Column(db.Float)

    opening_hours = db.relationship('OpeningHours', cascade="delete, delete-orphan")


class StockLevels(db.Model):
    """
    @author: Sol Clay

    Models the stock_levels table:
    Stores information about the stock level of each category of item for each food bank
    2 is high stock, 1 is low stock, 0 is urgent
    Also stores the bounds for stock level rankings
    auto_managed represent whether the food bank want to have their stock levels set manually or automatically, based
    on item stock
    """

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


class Stocks(db.Model):
    """
    @author: Sol Clay

    Models the stocks association table that associates
    the food_bank and item tables
     """
    fb_id = db.Column(db.Integer, db.ForeignKey('food_bank.id'), primary_key=True)
    item_id = db.Column(db.Integer, db.ForeignKey("item.id"), primary_key=True)
    quantity = db.Column(db.Integer, nullable=False)

    food_bank = db.relationship('FoodBank', backref=db.backref('items'))
    item = db.relationship('Item', backref=db.backref('stocked_at'))


# associate table models any user association with a food bank
associate = db.Table('associate',
                     db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
                     db.Column('fb_id', db.Integer, db.ForeignKey('food_bank.id'), primary_key=True))
