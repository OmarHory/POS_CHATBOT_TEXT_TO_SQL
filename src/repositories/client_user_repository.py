
import os, sys
from datetime import datetime
from sqlalchemy.orm import sessionmaker

parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(parent_dir)
from models.models import ClientUser


class ClientUserRepository:
    def __init__(self, sql_engine):
        self.sql_engine = sql_engine
        self.session = None

    def get_by_user_id(self, user_id):
        session = sessionmaker(bind=self.sql_engine)()
        result = session.query(ClientUser).filter(ClientUser.user_id == user_id).all()
        session.close()
        return result

    def get_by_client_id(self, client_id):
        session = sessionmaker(bind=self.sql_engine)()
        result = session.query(ClientUser).filter(ClientUser.client_id == client_id).all()
        session.close()
        return result

    def get_by_user_id_and_client_id(self, user_id, client_id):
        session = sessionmaker(bind=self.sql_engine)()
        result = session.query(ClientUser).filter(ClientUser.user_id == user_id, ClientUser.client_id == client_id).first()
        session.close()
        return result

    def create(self, user_id, client_id):
        session = sessionmaker(bind=self.sql_engine)()
        client_user = ClientUser(user_id=user_id, client_id=client_id, created_at=datetime.now())
        session.add(client_user)
        session.commit()
        session.close()
        return client_user

    def delete(self, client_user):
        session = sessionmaker(bind=self.sql_engine)()
        session.delete(client_user)
        session.commit()
        session.close()
