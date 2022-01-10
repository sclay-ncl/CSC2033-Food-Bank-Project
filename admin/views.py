from collections import Counter

from flask import render_template, flash, Blueprint
from flask_login import login_required
from werkzeug.security import generate_password_hash

from admin.forms import FoodBankRegistrationForm
from app import requires_roles, db
from models import User, FoodBank

admin_blueprint = Blueprint('admin', __name__, template_folder='templates')


def delete_log(file, line_delete):
    count = len(open(file).readlines())

    line_delete = int(count) - int(line_delete)

    """ Removes a given line from a file """
    with open(file, 'r') as read_file:
        lines = read_file.readlines()

    current_line = 1
    with open(file, 'w') as write_file:
        for line in lines:
            if current_line == line_delete:
                pass
            else:
                write_file.write(line)

            current_line += 1


def get_logs():
    # opens log file
    with open('admin-logs/admin-log.log', "r") as f:
        # selects the last 10 and then reverses the order
        content = f.read().splitlines()
        content.reverse()

    logs_info = []
    for log in content:
        log_split = log.split(",")
        logs_info.append(log_split)

    return logs_info


def get_log_graph_data():
    with open('admin-logs/admin-log.log', "r") as f:
        content = f.read().splitlines()

    logs_info = []
    for log in content:
        log_split = log.split(",")
        logs_info.append(log_split)

    date_data = []
    for log in range(len(logs_info)):
        date_data.append(logs_info[log][0])

    counter = Counter(date_data)
    data = counter.items()

    graph_data = []
    for i in data:
        graph_data.append(i)

    labels = [row[0] for row in graph_data]
    values = [row[1] for row in graph_data]

    return labels, values


def get_no_visits():
    with open('admin-logs/application-visits', "r") as f:
        return f.readline()


def get_no_users():
    user_count = db.session.query(User).count()
    return user_count


def get_no_fb():
    fb_count = db.session.query(FoodBank).count()
    return fb_count


@admin_blueprint.route('/admin')
@login_required
@requires_roles('admin')
def admin():
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
