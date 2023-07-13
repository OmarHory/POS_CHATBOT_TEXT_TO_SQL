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

    sql_sales_results = pos_obj.execute_query(f"SELECT order_date, SUM(total_price) FROM order_headers where client_id = {client_id} and order_date >= CURDATE() - INTERVAL 30 DAY and order_date != CURDATE() GROUP BY order_date ORDER BY order_date ASC;")
    sql_products_results = pos_obj.execute_query(f"SELECT s.order_date as date, s.name as product_name, MAX(s.total_sales) AS product_total_sales FROM (SELECT order_headers.order_date, products.name, SUM(order_details.price) AS total_sales FROM order_details JOIN products ON products.id = order_details.product_id JOIN order_headers ON order_headers.id = order_details.order_header_id WHERE order_headers.order_date >= CURDATE() - INTERVAL 30 DAY AND order_headers.client_id = {client_id} GROUP BY order_headers.order_date, products.name) s GROUP BY s.order_date order by order_date;")
    
    if not len(sql_sales_results) and not len(sql_products_results):
        print(f"no sql results for client_id {client_id}.")
        continue

    client_type = settings['client_type']
    client_currency_short = settings['client_currency_short']


    prompt = f"""
    Given the following SQL Results for the single month sales of a {client_type} ({client_description}) historically until yesterday.

    Sales Data Schema:
        - date: Date of the sales - Datetime; in the format of YYYY-MM-DD.
        - total_sales: total sales on a specific date - Float; in the format of {client_currency_short} Currency.

    
    Products Data Schema:
        - date: Date of the product sales - Datetime; in the format of YYYY-MM-DD.
        - product_name: Name of the product - String.
        - product_total_sales: total sales of the product - Float; in the format of {client_currency_short} Currency.


    There are two columns [date, total sales (in {client_currency_short} Currency)].

    Analyze the SQL Results below in order to send a report to the {client_type} owner about yesterday's sales compared to the previous days, emphasizing on the following:
    - Make your report understandable and in a format to be sent directly to the {client_type} owner, include numbers and percentage, try to find insights that a human wouldn't find.
    - Compare yesterday's sales to the same day of the week in the previous weeks.
    - Give insights about the top products.
    - Do other useful comparisons to the previous days of the week.
    - Provide professional insights for {client_type} industry.
    - Add emojis to each paragraph (to be compatible with whatsapp)
    - Make the tone conversational (not an email format).
    - Your name is Rocko [Rocko is an AI Assistant who is an Astronaut that is all-knowing in {client_type} industry].
    - Paychecks are sent on the 1st of each month.

    SQL Results for Sales Data:

    <Start of SQL Results>
    {sql_sales_results}
    <End of SQL Results>

    SQL Results for Products Data:

    <Start of SQL Results>
    {sql_products_results}
    <End of SQL Results>


    """

    results = send_to_gpt(prompt, model_name='gpt-4')

    # client_users = client_user_repo.get_by_client_id(client_id)
    user_ids = [1]
    # for client_user in client_users:
    for user_id in user_ids:
        # user_id = client_user.user_id

        user = user_repo.get_user_by_id(user_id)
        user_name = user.name
        user_phone_number = user.phone_number

        final_results = f'A message to {user_name} - {client_name} \n\n' + results
        print(final_results)
        send_to_twilio(twilio_client, user_phone_number, final_results, twilio_phone_number)
        time.sleep(3)
