import os, sys
#import models from models/models.py
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(parent_dir)
from models.models import Client, ClientUser

class ClientRepository:
    def __init__(self, session):
        self.session = session
    def create_client(self, name, slug):
        client = Client(name=name, slug=slug)
        self.session.add(client)
        self.session.commit()
        self.session.close()
        return client
    
    def fetch_client(self, client_id):
        client = self.session.query(Client).filter(Client.id == client_id).first()
        self.session.close()
        return client

    def fetch_clients(self):
        clients = self.session.query(Client).all()
        self.session.close()
        return {client.id: client for client in clients}
    
    def delete_client(self, client_id):
        
        # Remove associations from client_user table
        self.session.query(ClientUser).filter(ClientUser.client_id == client_id).delete()
        
        # Delete the client
        client = self.session.query(Client).filter(Client.id == client_id).first()
        if client:
            self.session.delete(client)
            self.session.commit()
        
        self.session.close()

    def associate_user_to_client(self, user_id, client_id):

            
            client_user = ClientUser(user_id=user_id, client_id=client_id)
            self.session.add(client_user)
            self.session.commit()
            
            self.session.close()

