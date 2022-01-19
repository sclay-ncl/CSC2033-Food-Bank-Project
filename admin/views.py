from collections import Counter

from flask import render_template, flash, Blueprint
from flask_login import login_required
from werkzeug.security import generate_password_hash

from admin.forms import FoodBankRegistrationForm
from app import requires_roles, db
from models import User, FoodBank

admin_blueprint = Blueprint('admin', __name__, template_folder='templates')


def delete_log(file, line_delete):
    """
    @author: Anthony Clermont
    Function deletes a log from log file

    @param: file, the file path for the file to delete from
    @param: line_delete, the index of the line to be deleted
    """
    count = len(open(file).readlines())

    # Because the logs are displayed in descending order of date (newest at the front) the code
    # needs to flip this to find the correct line to delete
    line_delete = int(count) - int(line_delete)

    # Reads the lines of the file
    with open(file, 'r') as read_file:
        lines = read_file.readlines()

    # Searches through each line adding it into the log file but will skip if it is the line to delete
    current_line = 1
    with open(file, 'w') as write_file:
        for line in lines:
            if current_line == line_delete:
                pass
            else:
                write_file.write(line)

            current_line += 1


def get_logs():
    """
    @author: Anthony Clermont
    Function gets all the log data

    @return: returns all log data in an array
    """
    # Opens log file
    with open('admin-logs/admin-log.log', "r") as f:
        # selects all the line and reverses the order
        content = f.read().splitlines()
        content.reverse()

    # Put all log data into array splitting each element of the log by comma so data can be used
    logs_info = []
    for log in content:
        log_split = log.split(",")
        logs_info.append(log_split)

    return logs_info


def get_log_graph_data():
    """
    @author: Anthony Clermont
    Function organises data for graph

    @return: returns tuple containing data for the rows and columns of the graph
    """
    # Opens log file
    with open('admin-logs/admin-log.log', "r") as f:
        content = f.read().splitlines()

    # Put all log data into array splitting each element of the log by comma so data can be used
    logs_info = []
    for log in content:
        log_split = log.split(",")
        logs_info.append(log_split)

    # Filtering out the log data we dont need, will keep the date the log occurred
    date_data = []
    for log in range(len(logs_info)):
        date_data.append(logs_info[log][0])

    # Counter functions creates dictionary of how many errors occurred on each day
    counter = Counter(date_data)
    data = counter.items()

    # Create array containing finalised graph data
    graph_data = []
    for i in data:
        graph_data.append(i)

    # Sort graph data into the x and y axis for the line graph
    labels = [row[0] for row in graph_data]
    values = [row[1] for row in graph_data]

    return labels, values


def get_no_visits():
    """
    @author: Anthony Clermont
    Function gets the number of visits to the application

    @return: returns the number of visits to the application
    """
    with open('admin-logs/application-visits', "r") as f:
        return f.readline()


def get_no_users():
    """
    @author: Anthony Clermont
    Function gets the number of users registered

    @return: returns the number of users registered
    """
    user_count = db.session.query(User).count()
    return user_count


def get_no_fb():
    """
    @author: Anthony Clermont
    Function gets the number of food banks registered

    @return: returns the number of food banks registered
    """
    fb_count = db.session.query(FoodBank).count()
    return fb_count


@admin_blueprint.route('/admin')
@login_required
@requires_roles('admin')
def admin():
    """
    @author: Anthony Clermont
    Renders the form for admin dashboard
    """
    graph_data = get_log_graph_data()
    return render_template('admin.html',
                           no_logs=len(get_logs()),
                           no_visits=get_no_visits(),
                           no_users=get_no_users(),
                           no_fb=get_no_fb(),
                           labels=graph_data[0],
                           values=graph_data[1])


@admin_blueprint.route('/logs', methods=['POST'])
@login_required
@requires_roles('admin')
def logs():
    """
    @author: Anthony Clermont
    Collects log data to display
    """
    # Call function to get graph data
    graph_data = get_log_graph_data()
    return render_template('admin.html',
                           logs=get_logs(),
                           no_logs=len(get_logs()),
                           no_visits=get_no_visits(),
                           no_users=get_no_users(),
                           no_fb=get_no_fb(),
                           labels=graph_data[0],
                           values=graph_data[1])


@admin_blueprint.route('/log-delete/<row_data>')
@login_required
@requires_roles('admin')
def log_delete(row_data):
    """
    @author: Anthony Clermont
    Deletes log from file
    """
    delete_log('admin-logs/admin-log.log', str(row_data))

    graph_data = get_log_graph_data()
    return render_template('admin.html',
                           logs=get_logs(),
                           no_logs=len(get_logs()),
                           no_visits=get_no_visits(),
                           no_users=get_no_users(),
                           no_fb=get_no_fb(),
                           labels=graph_data[0],
                           values=graph_data[1])


@admin_blueprint.route('/food-bank-registration', methods=['GET', 'POST'])
@login_required
@requires_roles('admin')
def food_bank_registration():
    """
    @author: Sol Clay
    Allows admin users to register a new food bank on the database, creates a food_bank user account associated with
    the food bank
    """
    form = FoodBankRegistrationForm()

    if form.validate_on_submit():  # check if email is already used in the database
        user = User.query.filter_by(email=form.email.data).first()

        if user:
            flash("Email Already Used", 'danger')
            return render_template('food-bank-registration.html', form=form)

        new_food_bank = FoodBank(name=form.name.data,
                                 email=form.email.data,
                                 phone_number=form.phone_number.data,
                                 website=form.website.data)

        new_user = User(email=form.email.data,  # creates user to manage the food bank
                        first_name=form.name.data,
                        last_name="N/A",
                        password=generate_password_hash(form.password.data),
                        phone_number=form.phone_number.data,
                        role='food_bank')

        new_food_bank.associated.append(new_user)  # associates the user account with the food bank
        db.session.add(new_food_bank)
        db.session.add(new_user)
        db.session.commit()

    return render_template('food-bank-registration.html', form=form)
