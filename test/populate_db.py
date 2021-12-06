import csv
import time
from app import db
from models import User, FoodBank, Item, OpeningHours, Address


def csv_to_list(file, start_index=0):
    with open(file, mode='r') as f:
        csv_data = csv.reader(f)
        output = [line[start_index:] for line in csv_data]
    return output


def convert_to_object(data, object_type):
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
            objects.append(FoodBank(name=attr[0],
                                    email=attr[1],
                                    phone_number=attr[2],
                                    website=attr[3]))
        elif object_type == "item":
            objects.append(Item(name=attr[0],
                                category=attr[1]))
        elif object_type == "opening_hours":
            objects.append(OpeningHours(address_id=int(attr[0]),
                                        day=attr[1],
                                        open_time=attr[2],
                                        close_time=attr[3]))
        elif object_type == "address":
            objects.append(Address(fb_id=int(attr[0]),
                                   building_name=attr[1],
                                   number_and_road=attr[2],
                                   town=attr[3],
                                   post_code=attr[4]))
    return objects


def add_to_db(object_list):
    for i in object_list:
        db.session.add(i)


def init_db():
    db.drop_all()
    db.create_all()
    data = {"user": csv_to_list(file="db data/user.csv", start_index=1),
            "food_bank": csv_to_list(file="db data/food_bank.csv", start_index=1),
            "item": csv_to_list(file="db data/item.csv", start_index=1),
            "address": csv_to_list(file="db data/address.csv", start_index=1),
            "opening_hours": csv_to_list(file="db data/opening_hours.csv", start_index=0)}
    for key in data:
        add_to_db(convert_to_object(data.get(key), key))
    db.session.commit()


if __name__ == '__main__':
    init_db()
