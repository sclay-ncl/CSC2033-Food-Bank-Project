import smtplib
from email.message import EmailMessage

from flask import url_for


def send(subject, email_text, recip):
    """
    @author: Anthony Clermont, Nathan Hartley
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
        smtp.login('noreply.feedingnewcastle@gmail.com', 'FeedingNewcastle22')
        smtp.send_message(message)


def send_mail(food_bank_id, msg):
    """
    @author: Nathan Hartley
    Function constructs the needed stock email

    @param: food_bank_id, the id of the food bank which needs the food
    @param: msg, message to send
    """
    from models import FoodBank  # to avoid circular imports

    food_bank = FoodBank.query.filter_by(id=food_bank_id).first()
    emails = [user.email for user in food_bank.associated if user.role == "donor"]

    subject = 'URGENT DONATIONS NEEDED'

    for email in emails:
        send(subject, msg, email)


def send_reset_email(user):
    """
    @author: Anthony Clermont
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
