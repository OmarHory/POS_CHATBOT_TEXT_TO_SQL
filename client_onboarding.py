# Get the client information from S3 in the main directory of the client ID.
# Reads the latest incremental ID in the clients table.
# Pulls the data for a new client.
# Writes raw data partitions to S3 --> client_id/raw/
# Prepare the data by running prepare_data.py
# Writes prepared data partitions to S3 --> client_id/processed/
# Write the client id and other metadata to the clients table.
# Add the user(s) to the users table (let there be a text or yaml file that contains the user(s) data and client data).
# Do the mapping of the user(s) to the client(s) in the user_client_mapping table.
# Run pos_driver.py to populate the POS data into the rocko database.

import subprocess
from datetime import datetime
import os,sys
import yaml
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
import argparse
from src.helpers.utils import create_directories
from src.repositories.client_repository import ClientRepository
from src.repositories.user_repository import UserRepository
from src.s3_handler import S3Handler

# Parse command-line arguments
parser = argparse.ArgumentParser()
parser.add_argument("--s3-onboarding-folder", type=int, required=True, help="a folder path in S3 that contains the client information")
args = parser.parse_args()
s3_onboarding_folder = args.client_id

load_dotenv()

db_uri = os.getenv("DATABASE_URI")
aws_secret_access_key = os.getenv("aws_secret_access_key")
aws_access_key_id = os.getenv("aws_access_key")

engine = create_engine(db_uri)
session = sessionmaker(bind=engine)

client_repo = ClientRepository(session=session())

with engine.connect() as connection:
    result = connection.execute(text("SELECT AUTO_INCREMENT FROM information_schema.TABLES WHERE TABLE_SCHEMA = :schema AND TABLE_NAME = :table"), schema='rocko', table='clients')
    next_id = result.scalar()
print(next_id)

create_directories(next_id)

s3_obj = S3Handler(aws_access_key_id, aws_secret_access_key)
s3_obj.download_files(f"s3-onboarding-folder", s3_onboarding_folder, f'data/{next_id}/raw', ['client_information.yaml'])


# Get command-line arguments

with open('client_information.yaml', 'r') as file:
    client_information = yaml.safe_load(file)
client_information['settings']['client_id'] = next_id
print(client_information)

client_repo.create_client(name=client_information['name'], slug=client_information['slug'], token=client_information['token'], settings=client_information['settings'], created_at=datetime.now(), updated_at=datetime.now(), deleted_at=None)

