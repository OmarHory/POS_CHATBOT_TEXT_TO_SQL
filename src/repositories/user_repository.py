from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os, sys
#import models from models/models.py
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(parent_dir)
from models import User

class UserRepository:
    def __init__(self, db_uri):
        self.engine = create_engine(db_uri)
        self.Session = sessionmaker(bind=self.engine)
    
    def get_user_by_id(self, user_id):
        session = self.Session()
        user = session.query(User).filter(User.id == user_id).first()
        session.close()
        return user
    
    def get_user_by_email(self, email):
        session = self.Session()
        user = session.query(User).filter(User.email == email).first()
        session.close()
        return user
    
    def get_user_by_phone_number(self, phone_number):
        session = self.Session()
        user = session.query(User).filter(User.phone_number == phone_number).first()
        session.close()
        return user
    
    def create_user(self, name, email, phone_number):
        session = self.Session()
        user = User(name=name, email=email, phone_number=phone_number)
        session.add(user)
        session.commit()
        session.close()
        return user
    
    def update_user(self, user_id, name=None, email=None, phone_number=None):
        session = self.Session()
        user = session.query(User).filter(User.id == user_id).first()
        
        if user:
            if name:
                user.name = name
            if email:
                user.email = email
            if phone_number:
                user.phone_number = phone_number

            session.commit()
        
        session.close()
        return user
    
    def delete_user(self, user_id):
        session = self.Session()
        user = session.query(User).filter(User.id == user_id).first()
        
        if user:
            session.delete(user)
            session.commit()
        
        session.close()
