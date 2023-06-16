from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os, sys
#import models from models/models.py
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(parent_dir)
from models.models import User

class UserRepository:
    def __init__(self, session):
        self.session = session
    
    def get_user_by_id(self, user_id):
        user = self.session.query(User).filter(User.id == user_id).first()
        self.session.close()
        return user
    
    def get_user_by_email(self, email):
        
        user = self.session.query(User).filter(User.email == email).first()
        self.session.close()
        return user
    
    def get_user_by_phone_number(self, phone_number):
        
        user = self.session.query(User).filter(User.phone_number == phone_number).first()
        self.session.close()
        return user
    
    def create_user(self, name, email, phone_number):
        
        user = User(name=name, email=email, phone_number=phone_number)
        self.session.add(user)
        self.session.commit()
        self.session.close()
        return user
    
    def update_user(self, user_id, name=None, email=None, phone_number=None):
        
        user = self.session.query(User).filter(User.id == user_id).first()
        
        if user:
            if name:
                user.name = name
            if email:
                user.email = email
            if phone_number:
                user.phone_number = phone_number

            self.session.commit()
        
        self.session.close()
        return user
    
    def delete_user(self, user_id):
        
        user = self.session.query(User).filter(User.id == user_id).first()
        
        if user:
            self.session.delete(user)
            self.session.commit()
        
        self.session.close()
