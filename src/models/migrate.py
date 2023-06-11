from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base
##
import os, sys

parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(parent_dir)
##
from config import config_gpt_sqlchemy, config_mysql, config_databases
from dotenv import load_dotenv

# Load environment variables from the .env file
load_dotenv()


DATABASE_URI = os.getenv("DATABASE_URI")

def apply_migrations():
    # Create the database engine
    engine = create_engine(DATABASE_URI)

    # Bind the engine to a session
    Session = sessionmaker(bind=engine)
    session = Session()

    # Create the tables
    Base.metadata.create_all(bind=engine)

    # Close the session
    session.close()

    print("Migrations applied successfully.")
    
if __name__ == '__main__':
    apply_migrations()
