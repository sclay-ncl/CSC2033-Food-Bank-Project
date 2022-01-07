import smtplib
from email.message import EmailMessage
from models import FoodBank
from flask import url_for


def send(subject, email_text, recip):
    message = EmailMessage()
    message['SUBJECT'] = subject
    message['From'] = 'noreply.feedingnewcastle@gmail.com'
    message['To'] = recip
    msg = email_text
    message.set_content(msg)

    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
        smtp.login('noreply.feedingnewcastle@gmail.com', 'FeedingNewcastle22')  # 'wfrdqalctmuzgcet'
        smtp.send_message(message)


def send_mail(food_bank_id, recip_list):
    food_bank = FoodBank.query.filter_by(id=food_bank_id).first()

    subject = 'EMERGENCY DONATIONS NEEDED'
    msg = FoodBank.generate_alerts(food_bank, urgent_categories='test')

    send(subject, msg, recip_list)


def send_reset_email(user):
    token = user.get_reset_token()

    subject = 'Password Reset Request'
    msg = f'''To reset your password, click the following link:
{ url_for('users.reset_token', token=token, _external=True) }
    
If this request was not made by you please email us: @feedingnewcastle@gmail.com.
'''
    send(subject, msg, user.email)





