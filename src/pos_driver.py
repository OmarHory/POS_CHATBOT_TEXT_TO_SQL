from repositories.pos_repository import PosRepository
import os

from dotenv import load_dotenv
load_dotenv()

client_id = os.getenv("client_id")

obj = PosRepository(os.getenv("DATABASE_URI"))
print(obj)
obj.insert_data(client_id, 'branches.csv', 'branches')
obj.insert_data(client_id, 'categories.csv', 'categories')
obj.insert_data(client_id, 'products.csv', 'products')
obj.insert_data(client_id, 'order_header.csv', 'order_headers')
obj.insert_data(client_id, 'order_details.csv', 'order_details')

obj.close_session()
