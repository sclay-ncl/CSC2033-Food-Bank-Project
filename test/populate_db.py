import csv
import time

from models import User, FoodBank, Item, OpeningHours, Address


def convert_to_user(file):
    users = []
    with open(file, mode='r') as f:
        csv_f = csv.reader(f)  # opens file in csv reader
        lines = [line[1:] for line in csv_f]  # omits the first column - id, as it is auto-assigned when added to db
    for i in range(1, len(lines)):
        attr = lines[i]
        new_user = User(role=attr[0],
                        first_name=attr[1],
                        last_name=attr[2],
                        email=attr[3],
                        phone_number=attr[4],
                        password=attr[5])
        users.append(new_user)
    return users


def convert_to_food_bank(file):
    food_banks = []
    with open(file, mode='r') as f:
        csv_f = csv.reader(f)
        lines = [line[1:] for line in csv_f]
    for i in range(1, len(lines)):
        attr = lines[i]
        new_food_bank = FoodBank(name=attr[0],
                                 email=attr[1],
                                 phone_number=attr[2],
                                 website=attr[3])
        food_banks.append(new_food_bank)
    return food_banks


def convert_to_item(file):
    items = []
    with open(file, mode='r') as f:
        csv_f = csv.reader(f)
        lines = [line[1:] for line in csv_f]
    for i in range(1, len(lines)):
        attr = lines[i]
        new_item = Item(name=attr[0],
                        category=attr[1])
        items.append(new_item)
    return items


def convert_to_opening_hours(file):
    opening_hours = []
    with open(file, mode='r') as f:
        csv_f = csv.reader(f)
        lines = [line for line in csv_f]
    for i in range(1, len(lines)):
        attr = lines[i]
        new_opening_hours = OpeningHours(address_id=int(attr[0]),
                                         day=attr[1],
                                         open_time=time.strptime(attr[2], '%I:%M'),
                                         close_time=time.strptime(attr[3], '%I:%M'))
        opening_hours.append(new_opening_hours)
    return opening_hours


def convert_to_address(file):
    with open(file, mode='r') as f:
        csv_f = csv.reader(file)


if __name__ == '__main__':
    users = convert_to_opening_hours('db data/opening_hours.csv')
