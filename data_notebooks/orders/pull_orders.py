import os
import argparse
from dotenv import load_dotenv
from utils import call_foodics

# Load environment variables from .env file
load_dotenv()

# Parse command-line arguments
parser = argparse.ArgumentParser()
parser.add_argument('--client-id', type=int, required=True, help='Client ID')
args = parser.parse_args()

# Get environment variables
token = os.getenv('data_access_token')
client_id = args.client_id

# Set filter
filter_ = {}

includables = 'branch,products.product,products.options.modifier_option'
# Call the foodics api to get the orders
last_page = call_foodics('orders', 1, client_id, token, includables=includables, filter=filter_, return_last_page=True)
print('last_page:', last_page)

call_foodics('orders', last_page, client_id, token, includables=includables, filter=filter_, checkpoint_every=2)
