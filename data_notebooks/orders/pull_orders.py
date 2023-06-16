import os
import argparse
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import sys
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
sys.path.append(parent_dir)

from src.repositories.client_repository import ClientRepository

from utils import call_foodics

# Load environment variables from .env file
load_dotenv()

# Parse command-line arguments
parser = argparse.ArgumentParser()
parser.add_argument('--client-id', type=int, required=True, help='Client ID')
args = parser.parse_args()

# Get environment variables
client_id = args.client_id

# Get Foodics API token from clients table
engine = create_engine(os.environ['DATABASE_URI'])
session = sessionmaker(bind=engine)
client_repo = ClientRepository(session=session())
client = client_repo.fetch_client(client_id)
token = client.token

# Set filter
filter_ = {}

includables = 'branch,products.product,products.options.modifier_option'
# Call the foodics api to get the orders
last_page = call_foodics('orders', 1, client_id, token, includables=includables, filter=filter_, return_last_page=True)
print('last_page:', last_page)

call_foodics('orders', last_page, client_id, token, includables=includables, filter=filter_, checkpoint_every=300)
