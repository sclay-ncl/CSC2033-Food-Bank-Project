import csv
import random
from datetime import datetime

from werkzeug.security import generate_password_hash

from app import db
from models import User, FoodBank, Item, OpeningHours, Address, Stocks, StockLevels


def csv_to_list(file, start_index=0):
    """
    @author: Sol Clay

    Converts data stored in csv files into a list of lists that contain the database field data

    @param file: the csv file containing the data
    @param start_index: defines which column the list should begin at
    @return output: a list of lists, each list containing the field data for one table row """

    with open(file, mode='r') as f:
        csv_data = csv.reader(f)
        output = [line[start_index:] for line in csv_data]
    return output


def convert_to_object(data, object_type):
    """
    @author: Sol Clay, Anthony Clermont

    Converts database field data stored in lists into sqlalchemy models

    @param: data, the data stored in lists
    @param: object_type, the model to which the data should be converted to

    @return: list of sqlalchemy model objects
    """
    objects = []
    for i in range(1, len(data)):
        attr = data[i]
        if object_type == "user":
            objects.append(User(role=attr[0],
                                first_name=attr[1],
                                last_name=attr[2],
                                email=attr[3],
                                phone_number=attr[4],
                                password=generate_password_hash(attr[5]),
                                number_and_road=attr[6],
                                town=attr[7],
                                postcode=attr[8],
                                long=attr[10],
                                lat=attr[9]))

        elif object_type == "food_bank":
            new_food_bank = FoodBank(id=int(attr[0]),
                                     name=attr[1],
                                     email=attr[2],
                                     phone_number=attr[3],
                                     website=attr[4])
            new_user = User(email=attr[2],  # creates user to manage the food bank
                            first_name=attr[1],
                            last_name="N/A",
                            password=generate_password_hash(password="password"),
                            phone_number=attr[3],
                            role='food_bank')
            new_user.associated.append(new_food_bank)  # creates association between the managing user and the food bank
            objects.append(new_food_bank)
            objects.append(new_user)

        elif object_type == "item":
            objects.append(Item(id=attr[0],
                                name=attr[1],
                                category=attr[2]))
        elif object_type == "opening_hours":
            objects.append(OpeningHours(address_id=int(attr[0]),
                                        day=attr[1],
                                        open_time=datetime.strptime(attr[2], "%H:%M").time(),
                                        close_time=datetime.strptime(attr[3], "%H:%M").time()))
        elif object_type == "address":
            objects.append(Address(id=attr[0],
                                   fb_id=attr[1],
                                   building_name=attr[2],
                                   number_and_road=attr[3],
                                   town=attr[4],
                                   postcode=attr[5],
                                   lat=attr[6],
                                   long=attr[7]))
    return objects


def generate_stocks(low, high):
    """
    @author: Sol Clay
    Generates instances of the association table Stocks with a bounded random quantity

    @param low: lower bound for stock count
    @param high: upper bound for stock count
    """
    items_count = db.session.query(Item).count()
    food_bank_count = db.session.query(FoodBank).count()
    for f in range(1, food_bank_count + 1):
        for i in range(1, items_count + 1):
            quantity = random.randrange(low, high)
            db.session.add(Stocks(fb_id=f, item_id=i, quantity=quantity))
    db.session.commit()


def generate_notify():
    """"
    @author: Sol Clay
    Generates instances of the association table notify for each user with the role donor, picking a random food bank
    """
    donor_users = User.query.filter_by(role="donor").all()
    food_banks = FoodBank.query.all()
    for user in donor_users:
        user.associated.append(random.choice(food_banks))
    db.session.commit()


def generate_stock_levels():
    """
    @author: Sol Clay
    Generates a stock_levels table for each food bank
    """
    food_banks = FoodBank.query.all()
    for f in food_banks:
        db.session.add(StockLevels(fb_id=f.id))
        f.update_stock_levels()
    db.session.commit()


def add_to_db(object_list):
    """
    @author: Sol Clay
    Iterates through a list of objects and adds them to the database session

    @param object_list: list of sqlalchemy models
    """
    for i in object_list:
        db.session.add(i)


def pop_db():
    """
    @author: Sol Clay
    Populates the database with data, some randomly generated, some defined in csv files.
    """
    db.drop_all()
    db.create_all()
    data = {"user": csv_to_list(file="db data/new_user.csv", start_index=1),
            "food_bank": csv_to_list(file="db data/food_bank.csv", start_index=0),
            "item": csv_to_list(file="db data/item.csv", start_index=0),
            "address": csv_to_list(file="db data/address.csv", start_index=0),
            "opening_hours": csv_to_list(file="db data/opening_hours.csv", start_index=0)}
    for key in data:
        add_to_db(convert_to_object(data.get(key), key))
    db.session.commit()
    generate_stocks(1, 10)
    generate_notify()
    generate_stock_levels()


if __name__ == '__main__':
    pop_db()
