from sqlalchemy import create_engine, Column, Integer, String, Float, Date, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

##
import os, sys

parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(parent_dir)
##
from config import config_gpt_sqlchemy, config_mysql, config_databases
import pandas as pd
import os


db_link = config_gpt_sqlchemy["database"].format(
    config_mysql["user"],
    config_mysql["password"].replace("@", "%40"),
    config_mysql["host"],
    config_mysql["port"],
    config_databases["data"],
)

print("SQL Engine created for Data...")
data_engine = create_engine(db_link)

# create a session factory
Session = sessionmaker(bind=data_engine)

Base = declarative_base()


class OrdersTable(Base):
    __tablename__ = "orders_gpt"
    date = Column(Date, primary_key=True)
    hour = Column(Integer, primary_key=True)
    day_name = Column(String(10), primary_key=True)
    is_weekend = Column(String(5), primary_key=True)
    month = Column(Integer, primary_key=True)
    year = Column(Integer, primary_key=True)
    type = Column(String(20), primary_key=True)
    source = Column(String(20), primary_key=True)
    cashflow = Column(Float(precision=2))


def insert_data(csv_name, table_name, engine):
    Session = sessionmaker(bind=engine)
    session = Session()
    dirname = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    filename = os.path.join(dirname, f"data/processed/{csv_name}")
    print(filename)
    df = pd.read_csv(filename)

    if table_name == "orders_gpt":
        for index, row in df.iterrows():
            session.add(
                OrdersTable(
                    date=pd.to_datetime(row["date"]),
                    hour=row["hour"],
                    day_name=row["day_name"],
                    is_weekend=row["is_weekend"],
                    month=row["month"],
                    year=row["year"],
                    type=row["type"],
                    source=row["source"],
                    cashflow=row["cashflow"]
                )
            )

    session.commit()
    session.close()


Base.metadata.create_all(data_engine)
