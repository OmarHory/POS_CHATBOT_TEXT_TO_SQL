from repositories.user_repository import UserRepository
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv
load_dotenv()

engine = create_engine(os.getenv("DATABASE_URI"))
Session = sessionmaker(bind=engine)
session = Session()
obj = UserRepository(session)
obj.create_user(name='Omar', email='omar@test.com', phone_number=962795704964)