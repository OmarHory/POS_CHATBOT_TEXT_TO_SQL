import os 
from src.repositories.client_repository import ClientRepository

from dotenv import load_dotenv
load_dotenv()

obj = ClientRepository(os.getenv("DATABASE_URI"))

def create_directories(client_repo):
    clients = client_repo.fetch_clients()

    # Loop through all clients
    for client_id in clients:
        dirs = [
            f"data/{client_id}",
            f"data/{client_id}/raw",
            f"data/{client_id}/processed",
            f"data/{client_id}/processed/updates",
            f"data/{client_id}/updates"
        ]

        for dir in dirs:
            if not os.path.exists(dir):
                os.makedirs(dir)

        os.chmod('data', 0o777)

create_directories(obj)