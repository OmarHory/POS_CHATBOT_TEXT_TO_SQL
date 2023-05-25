import pandas as pd
from config import config_twilio
from twilio.rest import Client
from helpers.predefined_report import get_general_report
from models.user import fetch_users
import time
import argparse

parser = argparse.ArgumentParser(description="Push notification to all users")
parser.add_argument(
    "--option",
    type=str,
    help="options: report, reminder",
    required=True,
    choices=["reminder", "report"],
)

args = parser.parse_args()


def push_notification(config_twilio, option):
    account_sid = config_twilio["account_sid"]
    auth_token = config_twilio["auth_token"]
    twilio_phone_number = config_twilio["twilio_phone_number"]
    client = Client(account_sid, auth_token)
    users = fetch_users()
    for key in users.keys():
        name = users[key]["name"]

        if option == "report":
            report = f"""\n\n----------------------------------\n\n{get_general_report()}\n\n----------------------------------\n\nIf you have any questions, please don't hesitate to reach out to me. I'm always here to help you out \U0001F600"""
            message = f"""Hey there _*{name}*_ \U0001F44B, this is _*Lex*_, your virtual assistant from Del Monte! I hope you're doing great today. Guess what? I've got some fantastic news to share with you! We have just released a brand new report on Avocados that I think you'll find quite interesting. So, are you ready to dive into this exciting topic with me? Let's get started!:"""
            image = config_twilio["avocado_smile_image"]
            send_message(client, twilio_phone_number, key, message, image)
            time.sleep(15)
            send_message(client, twilio_phone_number, key, report)

        elif option == "reminder":
            message = f"Hey {name}! It's your go-to AI Assistant, Lex, representing Del Monte! Just a quick reminder that I've got your back for any queries you may have.\n\nPlus, for all you active avocado aficionados out there, we're happy to report that we're sending out tri-weekly reports to keep you up-to-date on how Lex is enhancing your day-to-day operations. So keep on using Lex and let's keep crushing it together! :D"
            send_message(client, twilio_phone_number, key, message)


def send_message(client, twilio_phone_number, key, message, image=None):
    if image is not None:
        client.messages.create(
            from_=twilio_phone_number,
            to=f"whatsapp:{key}",
            media_url=image,
                body=message,
            )
    else:
        client.messages.create(
            from_=twilio_phone_number,
            to=f"whatsapp:{key}",
            body=message,
            )


push_notification(config_twilio, args.option)
