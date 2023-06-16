
import os, sys
import datetime

parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(parent_dir)
from models.models import ClientUser

class ClientUserRepository:
    def __init__(self, session):
        self.session = session

    def get_by_user_id(self, user_id):
        return self.session.query(ClientUser).filter(ClientUser.user_id == user_id)

    def get_by_client_id(self, client_id):
        return self.session.query(ClientUser).filter(ClientUser.client_id == client_id).first()

    def get_by_user_id_and_client_id(self, user_id, client_id):
        return self.session.query(ClientUser).filter(ClientUser.user_id == user_id, ClientUser.client_id == client_id).first()

    def create(self, user_id, client_id):
        client_user = ClientUser(user_id=user_id, client_id=client_id, created_at=datetime.now())
        self.session.add(client_user)
        self.session.commit()
        return client_user

    def delete(self, client_user):
        self.session.delete(client_user)
        self.session.commit()