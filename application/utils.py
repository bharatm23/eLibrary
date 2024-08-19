import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def send_email(address, subject, message):
    SMTP_SERVER_HOST = "localhost"
    SMTP_SERVER_PORT = 1025
    SENDER_EMAIL = "system@elibrary.com"
    SENDER_PASSWORD = "system"

    msg = MIMEMultipart('alternative')
    msg["From"] = SENDER_EMAIL
    msg["To"] = address
    msg["Subject"] = subject
    msg.attach(MIMEText(message, "html"))
   
    email = smtplib.SMTP(host=SMTP_SERVER_HOST, port=SMTP_SERVER_PORT)
    email.login(SENDER_EMAIL, SENDER_PASSWORD)
    email.send_message(msg)
    email.quit()
