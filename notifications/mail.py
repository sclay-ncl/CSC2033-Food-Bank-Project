import smtplib
from email.message import EmailMessage

from flask import url_for

from models import FoodBank, Associate, User


def send(subject, email_text, recip):
    """
        Function sends email(s)

        @param: subject, the email subject line
        @param: email_text, the email body
        @param: recip, the list of emails to send the email to

    """

    message = EmailMessage()
    message['SUBJECT'] = subject
    message['From'] = 'noreply.feedingnewcastle@gmail.com'
    message['To'] = recip
    msg = email_text
    message.set_content(msg)

    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
        smtp.login('noreply.feedingnewcastle@gmail.com', 'FeedingNewcastle22')  # 'wfrdqalctmuzgcet'
        smtp.send_message(message)


def send_mail(food_bank_id):
    """
        Function constructs the needed stock email

        @param: food_bank_id, the id of the food bank which needs the food

    """

    food_bank = FoodBank.query.filter_by(id=food_bank_id).first()
    recip_list_obj = Associate.query.filter_by(fb_id=food_bank_id).all()

    subject = 'EMERGENCY DONATIONS NEEDED'
    msg = FoodBank.generate_alerts(food_bank, urgent_categories='test')

    for i in range(len(recip_list_obj)):
        user = User.query.filter_by(id=recip_list_obj[i].user_id).first()

        send(subject, msg, user.email)


def send_reset_email(user):
    """
        Function constructs the reset email

        @param: user, the user object which has requested the password reset

        @var: token, the token used to authenticate the user

    """
    token = user.get_reset_token()

    subject = 'Password Reset Request'
    msg = f'''To reset your password, click the following link:
{ url_for('users.reset_token', token=token, _external=True) }
    
If this request was not made by you please email us: @feedingnewcastle@gmail.com.
'''
    send(subject, msg, user.email)





