import os, sys
#import models from models/models.py
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(parent_dir)
from models.models import Client, ClientUser
from sqlalchemy.orm import sessionmaker


class ClientRepository:
    def __init__(self, sql_engine):
        self.sql_engine = sql_engine

    def create_client(self, name, slug, token, settings, created_at, updated_at, deleted_at):
        session = sessionmaker(bind=self.sql_engine)()
        client = Client(name=name, slug=slug, token=token, settings=settings, created_at=created_at, updated_at=updated_at, deleted_at=deleted_at)
        session.add(client)
        session.commit()
        session.close()
        return client

    def fetch_client(self, client_id):
        session = sessionmaker(bind=self.sql_engine)()
        client = session.query(Client).filter(Client.id == client_id).first()
        session.close()
        return client

    def fetch_clients(self):
        session = sessionmaker(bind=self.sql_engine)()
        clients = session.query(Client).all()
        session.close()
        return clients
    
    def delete_client(self, client_id):
        session = sessionmaker(bind=self.sql_engine)()
        client_user = session.query(ClientUser).filter(ClientUser.client_id == client_id).delete()
        client = session.query(Client).filter(Client.id == client_id).first()
        if client:
            session.delete(client)
            session.commit()
        session.close()

    def associate_user_to_client(self, user_id, client_id):
        session = sessionmaker(bind=self.sql_engine)()
        client_user = ClientUser(user_id=user_id, client_id=client_id)
        session.add(client_user)
        session.commit()
        session.close()
