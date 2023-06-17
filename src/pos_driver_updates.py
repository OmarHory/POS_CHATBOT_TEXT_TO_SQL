import argparse
import os
import glob
from repositories.pos_repository import PosRepository
from helpers.utils import list_csv_files_in_directory
from dotenv import load_dotenv

def get_strings_with_prefix(lst, prefix):
    return [s for s in lst if s.startswith(prefix)]

load_dotenv()

# Parse command-line arguments
parser = argparse.ArgumentParser()
parser.add_argument("--client-id", type=int, required=True, help="Client ID")
args = parser.parse_args()

# Get command-line arguments
client_id = args.client_id


# Get environment variables
database_uri = os.getenv("DATABASE_URI")

# Create PosRepository object
pos_repo = PosRepository(database_uri)

path = f'data/{client_id}/processed/updates'
csv_files = list_csv_files_in_directory(path)

pos_repo.insert_data(client_id, 'branches.csv', 'branches', path)
pos_repo.insert_data(client_id, 'categories.csv', 'categories', path)
pos_repo.insert_data(client_id, 'products.csv', 'products', path)

prefixes = ['order_headers', 'order_details', 'order_options']

for prefix in prefixes:
    csvs = get_strings_with_prefix(csv_files, prefix)
    for csv_file in csvs:
        pos_repo.insert_data(client_id, csv_file, prefix, path)


pos_repo.close_session()


# Delete the CSV files
# for csv_file in csv_files:
#     os.remove(csv_file)
