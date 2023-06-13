import pandas as pd
import requests
import time
from datetime import date
pd.set_option('display.max_columns', None)
import os

from dotenv import load_dotenv
from utils import *

# Load environment variables from .env file
load_dotenv()

filter = {}

print('orders_final_include.csv does not exist')
includables = 'products,branch,products.product,tags,products.promotion,payments.payment_method,products.promotion,products.options,products.options.modifier_option'
# call the foodics api to get the orders
last_page = call_foodics('orders', 1, includables=includables, filter=filter, return_last_page=True)
print('last_page: ', last_page)

list_responses = call_foodics('orders', last_page, includables=includables, filter=filter)
df_orders = pd.DataFrame([item for sublist in list_responses for item in sublist])
df_orders.to_csv('data/orders_final_include.csv', index=False)
print(df_orders.shape)
