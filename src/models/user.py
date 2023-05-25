from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from config import config_gpt_sqlchemy, config_mysql, config_databases

# create the database engine
db_link = config_gpt_sqlchemy["database"].format(
    config_mysql["user"],
    config_mysql["password"].replace("@", "%40"),
    config_mysql["host"],
    config_mysql["port"],
    config_databases["users"],
)
print("SQL Engine created for User...")
user_engine = create_engine(db_link)

# create a session factory
Session = sessionmaker(bind=user_engine)

# create a base class for declarative models
Base = declarative_base()


# define a User model
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    phone_number = Column(String(255))
    email = Column(String(255))
    name = Column(String(255))


# fetch all users from the users table
def fetch_users():
    session = Session()
    users = session.query(User).all()
    users_dict = {
        user.phone_number: {"name": user.name, "email": user.email} for user in users
    }
    session.close()
    return users_dict


# fetch a single user by phone number
def fetch_user(phone_number):
    session = Session()
    user = session.query(User).filter_by(phone_number=phone_number).first()
    user_dict = {"name": user.name, "email": user.email} if user else None
    session.close()
    return user_dict


# insert a new user into the users table
def insert_user(phone_number, email, name):
    session = Session()
    new_user = User(phone_number=phone_number, email=email, name=name)
    session.add(new_user)
    session.commit()
    session.close()


def user_exists_by_email(email):
    session = Session()
    user = session.query(User).filter_by(email=email).first()
    print("user_exists_by_email: ", user)
    session.close()
    return user is not None


# close the database connection
def close_connection():
    Session().close_all()


Base.metadata.create_all(user_engine)
