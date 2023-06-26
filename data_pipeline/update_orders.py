import os
import argparse
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import sys
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(parent_dir)

from src.repositories.client_repository import ClientRepository
from src.repositories.pos_repository import PosRepository
from datetime import timedelta
import pandas as pd
import glob

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

db_uri = os.getenv("DATABASE_URI")
pos_repo = PosRepository(db_uri)
business_datetime = pos_repo.get_max_order_date(client_id)
# business_datetime = "2021-06-23 00:00:00"

business_date_after = (pd.to_datetime(business_datetime) - timedelta(days=1)).strftime("%Y-%m-%d")
business_datetime = str(business_datetime).replace(" ", '_')
business_datetime = str(business_datetime).replace(":", '_')

print('business_datetime:', business_datetime)

business_date_after = "2023-06-23"

# filter = {"business_date":business_date_after}

filter = {"business_date_after":business_date_after}

path = f'data/{client_id}/raw/updates'
# remove all files in the directory
files = glob.glob(f"{path}/*.csv")
for f in files:
    os.remove(f)

includables = "branch,products.product,products.options.modifier_option"
last_page = call_foodics("orders", 1, client_id, token, includables=includables, filter=filter, return_last_page=True)
call_foodics("orders", last_page, client_id, token, includables=includables, filter=filter, do_checkpoint=True, path_directory= f'data/{client_id}/raw/updates',postfix_name='updates')