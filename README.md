# Feeding Newcastle
> Project for CSC2033 Team 15,
> Git Repo [_here_](https://github.com/sclay-ncl/CSC2033-Food-Bank-Project).

## Table of Contents
* [General Info](#general-information)
* [Project Authors](#project-authors)
* [Technologies Used](#technologies-used)
* [Features](#features)
* [References](#references)
* [Setup](#setup)
* [Usage](#usage)


## General Information
This project's aim is to help with the UN's second sustainable goal of zero hunger. 
The project is a flask based web application aimed to aid all who utilise food banks;
For both people in need and wanting to help and food bank managers and volunteers

## Important Information ❗

The PayPal Donation button is live any donation made will go through to Feeding Newcastle's PayPal account.
If you would like to see the donation link working in full please watch the demonstration video.

## Project Authors
- Anthony Clermont
- Sol Clay
- Tess Goulandris
- Nate Hartley
- Alli Edwards


## Technologies Used
- [Python - version 3.8](https://www.python.org/)
- [Flask - version 2.0](https://flask.palletsprojects.com/en/2.0.x/)
- [SQL Alchemy - version 2.5.1](https://www.sqlalchemy.org/)
- [Mapbox API](https://www.mapbox.com/)


## Libraries Used
- [click](https://click.palletsprojects.com/en/8.0.x/)
- [Flask](https://flask.palletsprojects.com/en/2.0.x/)
- [ItsDangerous](https://itsdangerous.palletsprojects.com/en/2.0.x/)
- [Jinja2](https://jinja.palletsprojects.com/en/3.0.x/)
- [MarkupSafe](https://pypi.org/project/MarkupSafe/)
- [pip](https://pypi.org/project/pip/)
- [setuptools](https://pypi.org/project/setuptools/)
- [Werkzeug](https://pypi.org/project/Werkzeug/)
- [wheel](https://pypi.org/project/wheel/)
- [Flask-SQLAlchemy](https://flask-sqlalchemy.palletsprojects.com/en/2.x/)
- [SshTunnel](https://pypi.org/project/sshtunnel/)
- [Requests](https://docs.python-requests.org/en/latest/)
- [Flask-Login](https://flask-login.readthedocs.io/en/latest/)
- [Flask_wtf](https://flask-wtf.readthedocs.io/en/1.0.x/)
- [WTForms](https://wtforms.readthedocs.io/en/3.0.x/)
- [Uk-postcode-utils](https://pypi.org/project/uk-postcode-utils/)
- [Rfeed](https://pypi.org/project/rfeed/)
- [Email-validator](https://pypi.org/project/email-validator/)


## Application Pages
- Register and Login
  - Error Validation
  - Hashing Functionality
  - Email Password Reset Functionality
- Food Bank Search
  - Mapbox Api Usage to Display Key Data
  - Multi-Location Support
- Food Bank Information
  - Detailed Information Provided
  - Food Bank Category Stock Levels
- Contact
  - Useful Information
- Donate
  - Paypal Donation link 
- Profile
  - View/Edit Profile 
- Admin Dashboard
  - Overview of Key Application Data
  - View/Delete Error Logs
- Food Bank User
  - Add New Locations
  - Add/Remove Opening Times
  - View/Edit Food Bank Contact Information
  - Manual or Automatic Stock Boundaries
  - Stock Management

## References
This image has been used in the index page.  
![Example screenshot](./static/referance_image.jpg)  
Credits of this image: https://bonnydowns.org/foodbank/


## Setup

How to configure your local environment:

#### Local Environment
If you do not have a virtual environment (venv folder):  
1. Open a Terminal
2. CD into where the project is saved: ``` cd ProjectLocation ```
3. Create the virtualenv: ``` virtualenv -p python3 myenv ```
4. Activate the environment: ``` source myenv/bin/activate ```

#### Project Dependencies
To install the project's dependencies, run the following command:  
``` pip install -r requirements.txt ```

#### Interpreter Configuration
Please ensure your python interpreter configuration is working in the current directory.  
For more information about how to do this please visit your IDE's Documentation:
- [PyCharm](https://www.jetbrains.com/pycharm/learn/)
- [Visual Studio Code](https://code.visualstudio.com/docs)
- [Sublime Text](https://www.sublimetext.com/docs/)
- [Eclipse](https://www.eclipse.org/documentation/)

## Usage
To start the server and be able to run the application within your local environment:

Open a terminal, cd into the project directory if not already.   
Run the following command: ``` python app.py ```

Alternatively navigate to app.py file. Navigate to and run the line: 
```python 
if __name__ == '__main__': 
```
