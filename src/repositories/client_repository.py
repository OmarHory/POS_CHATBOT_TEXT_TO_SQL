from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os, sys
#import models from models/models.py
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(parent_dir)
from models.models import Client, ClientUser

class ClientRepository:
    def __init__(self, db_uri):
        self.engine = create_engine(db_uri)
        self.Session = sessionmaker(bind=self.engine)
    
    def create_client(self, name, slug):
        session = self.Session()
        client = Client(name=name, slug=slug)
        session.add(client)
        session.commit()
        session.close()
        return client
    
    def fetch_client(self, client_id):
        session = self.Session()
        client = session.query(Client).filter(Client.id == client_id).first()
        session.close()
        return client

    def fetch_clients(self):
        session = self.Session()
        clients = session.query(Client).all()
        session.close()
        return {client.id: client for client in clients}
    
    def delete_client(self, client_id):
        session = self.Session()
        
        # Remove associations from client_user table
        session.query(ClientUser).filter(ClientUser.client_id == client_id).delete()
        
        # Delete the client
        client = session.query(Client).filter(Client.id == client_id).first()
        if client:
            session.delete(client)
            session.commit()
        
        session.close()

    def associate_user_to_client(self, user_id, client_id):
            session = self.Session()
            
            client_user = ClientUser(user_id=user_id, client_id=client_id)
            session.add(client_user)
            session.commit()
            
            session.close()

