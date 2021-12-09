import csv
import random
from app import db
from models import User, FoodBank, Item, OpeningHours, Address, Stocks, StockLevels


def csv_to_list(file, start_index=0):
    """
    Converts data stored in csv files into a list of lists that contain the database field data

    :param file: the csv file containing the data
    :param start_index: defines which column the list should begin at
    :return output: a list of lists, each list containing the field data for one table row """

    with open(file, mode='r') as f:
        csv_data = csv.reader(f)
        output = [line[start_index:] for line in csv_data]
    return output

def convert_to_object(data, object_type):
    """
    Converts database field data stored in lists into sqlalchemy models

    :param data: the data stored in lists
    :param object_type: the model to which the data should be converted to
    :return list of sqlalchemy model objects
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
                                password=attr[5]))
        elif object_type == "food_bank":
            objects.append(FoodBank(id=int(attr[0]),
                                    name=attr[1],
                                    email=attr[2],
                                    phone_number=attr[3],
                                    website=attr[4]))
        elif object_type == "item":
            objects.append(Item(id=attr[0],
                                name=attr[1],
                                category=attr[2]))
        elif object_type == "opening_hours":
            objects.append(OpeningHours(address_id=int(attr[0]),
                                        day=attr[1],
                                        open_time=attr[2],
                                        close_time=attr[3]))
        elif object_type == "address":
            objects.append(Address(id=attr[0],
                                   fb_id=attr[1],
                                   building_name=attr[2],
                                   number_and_road=attr[3],
                                   town=attr[4],
                                   post_code=attr[5]))
    return objects

def generate_stocks(low, high):
    """
    Generates instances of the association table Stocks with a bounded random quantity

    :param low: lower bound for stock count
    :param high: upper bound for stock count
    """
    items_count = db.session.query(Item).count()
    food_bank_count = db.session.query(FoodBank).count()
    for f in range(1, food_bank_count+1):
        for i in range(1, items_count+1):
            quantity = random.randrange(low, high)
            db.session.add(Stocks(fb_id=f, item_id=i, quantity=quantity))
    db.session.commit()

def generate_notify():
    """"
    Generates instances of the association table notify for each user with the role donor, picking a random food bank
    """
    donor_users = User.query.filter_by(role="donor").all()
    food_banks = FoodBank.query.all()
    for user in donor_users:
        user.notify.append(random.choice(food_banks))
    db.session.commit()

def generate_stock_levels():
    """Generates a stock_levels table for each food bank"""
    food_banks = FoodBank.query.all()
    for f in food_banks:
        db.session.add(StockLevels(fb_id=f.id))
    db.session.commit()

def generate_appointments():  # need to design appointments system further
    pass

def add_to_db(object_list):
    """
    Iterates through a list of objects and adds them to the database session

    :param object_list: list of sqlalchemy models
    """
    for i in object_list:
        db.session.add(i)


def pop_db():
    """
    Populates the database with data, some randomly generated, some defined in csv files.
    """
    db.drop_all()
    db.create_all()
    data = {"user": csv_to_list(file="db data/user.csv", start_index=1),
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