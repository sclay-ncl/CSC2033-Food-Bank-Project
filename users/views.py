import requests
import urllib.parse
from flask_login import current_user, login_user, logout_user, login_required
from flask import redirect, url_for

""" 
Function returns the latitude and longitude of a given address
@param:address, address of desired latitude and longitude co-ordinates
@returns: tuple of latitude and longitude co-ordinates
"""
def get_lat_long(address):
    url = 'https://nominatim.openstreetmap.org/search/' + urllib.parse.quote(address) + '?format=json'
    response = requests.get(url).json()

    latitude = response[0]["lat"]
    longitude = response[0]["lon"]

    return latitude, longitude


def register():
    pass  # TODO: add register functionality


def login():
    pass  # TODO: add login functionality

def account():
    pass  # TODO:add account functionality

@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))
