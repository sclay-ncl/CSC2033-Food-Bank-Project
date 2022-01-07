import smtplib
from email.message import EmailMessage
from models import FoodBank, User
from flask import url_for


def send_mail():
    foodbank = FoodBank.query.filter_by(id=id).first()
    # user = User.query.filter_by(id=id).first().email

    message = EmailMessage()
    message['Subject'] = 'EMERGENCY DONATIONS NEEDED'
    message['From'] = 'noreply.feedingnewcastle@gmail.com'
    message['To'] = 'nathanhartley82@gmail.com'  # user
    msg = FoodBank.generate_alerts(FoodBank, urgent_categories='test')
    message.set_content(msg)

    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
        smtp.login('noreply.feedingnewcastle@gmail.com', 'FeedingNewcastle22')  # 'wfrdqalctmuzgcet'
        smtp.send_message(message)

    send_mail()


def send_reset_email(user):
    token = user.get_reset_token()

    # working
    gmail_user = 'FeedingNewcastle@gmail.com'
    gmail_password = 'Pea5NudeCure'

    sent_from = gmail_user
    to = [user.email]
    subject = 'Password Reset Request'
    body = f''' To reset your password, click the following link:
{ url_for('users.reset_token', token=token, _external=True) }
    
If this request was not made by you please email us: @feedingnewcastle@gmail.com.
'''
    email_text = """\
    From: %s
    To: %s
    Subject: %s

    %s
    """ % (sent_from, ", ".join(to), subject, body)

    server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
    server.ehlo()
    server.login(gmail_user, gmail_password)
    server.sendmail(sent_from, to, email_text)
    server.close()





