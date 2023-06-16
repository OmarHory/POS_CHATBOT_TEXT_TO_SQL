import argparse
from repositories.pos_repository import PosRepository
import os

from dotenv import load_dotenv

load_dotenv()

# Parse command-line arguments
parser = argparse.ArgumentParser()
parser.add_argument("--client-id", type=int, required=True, help="Client ID")
args = parser.parse_args()
# Get environment variables
client_id = args.client_id

obj = PosRepository(os.getenv("DATABASE_URI"))

obj.insert_data(client_id, "branches.csv", "branches")
obj.insert_data(client_id, "categories.csv", "categories")
obj.insert_data(client_id, "products.csv", "products")
obj.insert_data(client_id, "order_header.csv", "order_headers")
obj.insert_data(client_id, "order_details.csv", "order_details")
obj.insert_data(client_id, "options.csv", "order_options")

obj.close_session()
