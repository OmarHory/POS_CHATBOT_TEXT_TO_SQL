from sqlalchemy import (
    create_engine,
    Column,
    Integer,
    String,
    DateTime,
    Text,
    Float,
    Boolean,
    VARCHAR
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import datetime

##
import os, sys
import pandas as pd

parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(parent_dir)
##

from config import config_gpt_sqlchemy, config_mysql, config_databases

# create the database engine
db_link = config_gpt_sqlchemy["sqlchemy_database"].format(
    config_mysql["mysql_user"],
    config_mysql["mysql_password"].replace("@", "%40"),
    config_mysql["mysql_host"],
    config_mysql["mysql_port"],
    config_databases["mysql_db_log"],
)

Base = declarative_base()
print("SQL Engine created for Log...")

log_engine = create_engine(db_link)

# create a session factory
Session = sessionmaker(bind=log_engine)


class MessageLog(Base):
    __tablename__ = "user_activity"
    id = Column(Integer, primary_key=True)
    username = Column(String(30))
    phone_number = Column(String(30))
    input = Column(Text)
    output = Column(Text)
    user_intent = Column(String(30))
    message_type = Column(Text)
    sql_cmd = Column(Text)
    sql_result = Column(Text)
    error_flag = Column(Boolean)
    error_description = Column(Text)
    request_timestamp = Column(DateTime)
    response_timestamp = Column(DateTime)
    time_taken = Column(Float)
    input_type = Column(VARCHAR(20))

    def __repr__(self):
        return f"<MessageLog {self.id}: {self.phone_number} - {self.message_type} - {self.timestamp}>"


def log_user_message(
    username,
    phone_number,
    user_intent,
    input,
    output,
    message_type,
    sql_cmd,
    sql_result,
    error_flag,
    error_description,
    request_timestamp,
    response_timestamp,
    time_taken,
    input_type
):
    session = Session()

    message_log = MessageLog(
        username=username,
        phone_number=phone_number,
        user_intent=user_intent,
        input=input,
        output=output,
        message_type=message_type,
        sql_cmd=sql_cmd,
        sql_result=sql_result,
        error_flag=error_flag,
        error_description=error_description,
        request_timestamp=request_timestamp,
        response_timestamp=response_timestamp,
        time_taken=time_taken,
        input_type=input_type,
    )

    session.add(message_log)
    session.commit()
    session.close()


def insert_old_data(engine):
    Session = sessionmaker(bind=engine)
    session = Session()
    df = pd.read_sql("SELECT * FROM user_message_log", engine)
    for _, row in df.iterrows():
        session.add(
            MessageLog(
                phone_number=row["phone_number"],
                input=row["input"],
                output=row["output"],
                message_type="old_messages",
            )
        )

    session.commit()
    session.close()


# close the database connection
def close_connection():
    Session().close_all()


# Base.metadata.drop_all(log_engine)

Base.metadata.create_all(log_engine)

# insert_old_data(engine=log_engine)
