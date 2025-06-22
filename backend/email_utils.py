# backend/email_utils.py

import os
import smtplib
from email.mime.text import MIMEText
from sqlalchemy.orm import Session
from models import PriceAlert, TrackedProduct, User
from dotenv import load_dotenv

load_dotenv()

SENDER_EMAIL = os.getenv("EMAIL_USER")  
SENDER_PASSWORD = os.getenv("EMAIL_PASS") 

def send_email(to_email, subject, body):
    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = SENDER_EMAIL
    msg["To"] = to_email

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            server.sendmail(SENDER_EMAIL, [to_email], msg.as_string())
            print(f"[✉️] Email sent to {to_email}")
    except Exception as e:
        print(f"[❌] Failed to send email to {to_email}: {e}")


async def send_email_if_needed(product_id: int, current_price: float, db: Session):
    if current_price is None:
        return

    alerts = db.query(PriceAlert).filter_by(product_id=product_id, active=True).all()
    for alert in alerts:
        if current_price <= alert.target_price:
            user = db.query(User).filter_by(id=alert.user_id).first()
            product = db.query(TrackedProduct).filter_by(id=product_id).first()

            subject = f"📉 Price Drop Alert: {product.product_name}"
            body = (
                f"Hi {user.email},\n\n"
                f"The price for *{product.product_name}* has dropped to ₹{current_price}!\n"
                f"Your Target Price: ₹{alert.target_price}\n\n"
                f"Check it out here: {product.url}\n\n"
                f"— PricePulse Team"
            )

            send_email(user.email, subject, body)

            alert.active = False
            db.commit()
