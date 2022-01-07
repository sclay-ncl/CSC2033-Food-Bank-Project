import smtplib
from email.message import EmailMessage
from models import FoodBank, User


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
