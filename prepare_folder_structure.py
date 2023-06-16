import os
from src.repositories.client_repository import ClientRepository

# sqlalchemy
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from dotenv import load_dotenv

load_dotenv()


sql_engine = create_engine(
    os.getenv("DATABASE_URI"),
)
session = sessionmaker(bind=sql_engine)
session = session()
obj = ClientRepository(session)


def create_directories(client_repo):
    clients = client_repo.fetch_clients()
    if not len(clients):
        print("No clients found")
        return

    if not os.path.exists("data/"):
        os.makedirs("data/")
    # Loop through all clients
    for client_id in clients:
        dirs = [
            f"data/{client_id}",
            f"data/{client_id}/raw",
            f"data/{client_id}/raw/partitions",
            f"data/{client_id}/processed",
            f"data/{client_id}/processed/updates",
            f"data/{client_id}/updates",
        ]

        for dir in dirs:
            if not os.path.exists(dir):
                os.makedirs(dir)

        os.chmod("data", 0o777)


create_directories(obj)
