import requests
import urllib.parse

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
    pass


def login():
    pass


def logout():
    pass
