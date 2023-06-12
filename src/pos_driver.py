from models import models

# from repositories.client_repository import ClientRepository
# from repositories.user_repository import UserRepository
from repositories.pos_repository import PosRepository
# from repositories.log_repository import LogRepository


import os

from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# obj = ClientRepository(os.getenv("DATABASE_URI"))

obj = PosRepository(os.getenv("DATABASE_URI"))
print(obj)

obj.insert_data(1, 'order_header.csv', 'order_headers')