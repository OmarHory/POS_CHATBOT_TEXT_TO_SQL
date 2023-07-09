import time
import pandas as pd
import argparse
from src.repositories.pos_repository import PosRepository
from src.repositories.client_repository import ClientRepository
from src.repositories.client_user_repository import ClientUserRepository
from src.repositories.user_repository import UserRepository
import os
from src.gpt_api import send_to_gpt
from twilio.rest import Client
from src.helpers.utils import send_to_twilio
from sqlalchemy import create_engine


from dotenv import load_dotenv
load_dotenv()

import src.update_variables
from src.config import config_twilio
db_uri = os.getenv("DATABASE_URI")

print("db_uri is:", db_uri)

# # Parse command-line arguments
# parser = argparse.ArgumentParser()
# parser.add_argument("--client-id", type=int, required=True, help="Client ID")
# args = parser.parse_args()
# client_id = args.client_id

# twilio settings
account_sid = config_twilio["twilio_account_sid"]
auth_token = config_twilio["twilio_auth_token"]
twilio_phone_number = config_twilio["twilio_phone_number"]

engine = create_engine(db_uri)

user_repo = UserRepository(engine)
client_user_repo = ClientUserRepository(engine)
client_repo = ClientRepository(engine)

clients = client_repo.fetch_clients()
twilio_client = Client(account_sid, auth_token)
pos_obj = PosRepository(db_uri)

for client in clients:
    print("#####################\n\n")
    client_id = client.id

    client_name = client.name
    settings = client.settings
    if 'client_description' in settings:
        client_description = settings['client_description']
    else:
        client_description = ''
    print("client_description is:", client_description)

    sql_results = pos_obj.execute_query(f"SELECT order_date, SUM(total_price) FROM order_headers where client_id = {client_id} and order_date >= CURDATE() - INTERVAL 30 DAY and order_date != CURDATE() GROUP BY order_date ORDER BY order_date ASC;")
    
    if not len(sql_results):
        print(f"no sql results for client_id {client_id}.")
        continue
    client_type = settings['client_type']
    client_currency_short = settings['client_currency_short']


    prompt = f"""
    Given the following SQL Results for the single month sales of a {client_type} ({client_description}) historically until yesterday.
    There are two columns [date, total sales (in {client_currency_short} Currency)].

    Analyse the SQL Results below in order to send a report to the {client_type} owner about yesterday's sales compared to the previous days.

    - Make your report understandable and in a format to be sent directly to the {client_type} owner, include numbers and percentage, try to find insights that a human wouldn't find.
    - Provide professional insights in the field of F&B.
    - Add emojis to each paragraph (to be compatible with whatsapp)
    - Make the tone conversational (not an email format).
    - Your name is Rocko [Rocko is an AI Assistant who is an Astronaut that is all-knowing in the field of F&B and Retail].
    - Make the report less than 1500 characters.

    SQL Results for Sales Data:

    <Start of SQL Results>
    {sql_results}
    <End of SQL Results>
    """

    results = send_to_gpt(prompt, model_name='gpt-4')

    client_users = client_user_repo.get_by_client_id(client_id)
    # user_ids = [1,2,3,4,5]
    for client_user in client_users:
        user_id = client_user.user_id

        user = user_repo.get_user_by_id(user_id)
        user_name = user.name
        user_phone_number = user.phone_number

        final_results = f'A message to {user_name} - {client_name} \n\n' + results
        print(final_results)
        send_to_twilio(twilio_client, user_phone_number, final_results, twilio_phone_number)
        time.sleep(3)
