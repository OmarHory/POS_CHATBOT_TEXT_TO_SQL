from sqlalchemy import create_engine, Column, Integer, String, Float, Date, Boolean, DateTime, ForeignKey, Time
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


class OrderHeader(Base):
    __tablename__ = "order_header"
    order_header_id = Column(String(40), primary_key=True)
    branch_id = Column(String(40), ForeignKey("branches.branch_id"))
    order_time = Column(Time)
    order_date = Column(Date)
    order_type = Column(String(20))
    order_source = Column(String(20))
    order_status = Column(String(20))
    order_total_price = Column(Float(precision=2))

class OrderDetails(Base):
    __tablename__ = "order_details"
    order_details_id = Column(String(50), primary_key=True)
    order_header_id = Column(String(40), ForeignKey("order_header.order_header_id"))
    product_id = Column(String(40), ForeignKey("products.product_id"))
    category_id = Column(String(40), ForeignKey("categories.category_id"))
    quantity = Column(Integer)
    product_price = Column(Float(precision=2))

class Branches(Base):
    __tablename__ = "branches"
    branch_id = Column(String(40), primary_key=True)
    branch_name = Column(String(40))
    opening_from = Column(String(10))
    opening_to = Column(String(10))

class Products(Base):
    __tablename__ = "products"
    product_id = Column(String(40), primary_key=True)
    product_name = Column(String(150))
    product_sku = Column(String(40))
    category_id = Column(String(40), ForeignKey("categories.category_id"))
    category_name = Column(String(40))
    is_active = Column(Boolean)
    is_stock_product = Column(Boolean)
    price = Column(Float(precision=2))

class Categories(Base):
    __tablename__ = "categories"
    category_id = Column(String(40), primary_key=True)
    category_name = Column(String(40))


def insert_data(csv_name, table_name, engine):
    Session = sessionmaker(bind=engine)
    session = Session()
    dirname = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    filename = os.path.join(dirname, f"data/processed/{csv_name}")
    print(filename)
    df = pd.read_csv(filename)

    if table_name == "order_header":
        for index, row in df.iterrows():
            session.add(
                OrderHeader(
                    order_header_id=row["order_header_id"],
                    branch_id=row["branch_id"],
                    order_time=row["order_time"],
                    order_date=pd.to_datetime(row["order_date"]),
                    order_type=row["order_type"],
                    order_source=row["order_source"],
                    order_status=row["order_status"],
                    order_total_price=row["order_total_price"],
                )
            )
    
    if table_name == "order_details":
        for index, row in df.iterrows():
            session.add(
                OrderDetails(
                    order_details_id=row["order_details_id"],
                    order_header_id=row["order_header_id"],
                    product_id=row["product_id"],
                    category_id=row["category_id"],
                    quantity=row["quantity"],
                    product_price=row["product_price"],
                )
            )

    if table_name == "branches":
        for index, row in df.iterrows():
            session.add(
                Branches(
                    branch_id=row["branch_id"],
                    branch_name=row["branch_name"],
                    opening_from=row["opening_from"],
                    opening_to=row["opening_to"],
                )
            )
    
    if table_name == "products":
        for index, row in df.iterrows():
            session.add(
                Products(
                    product_id=row["product_id"],
                    product_name=row["product_name"],
                    product_sku=row["product_sku"],
                    category_id=row["category_id"],
                    category_name=row["category_name"],
                    is_active=row["is_active"],
                    is_stock_product=row["is_stock_product"],
                    price=row["price"],
                )
            )

    if table_name == "categories":

        for index, row in df.iterrows():
            session.add(
                Categories(
                    category_id=row["category_id"],
                    category_name=row["category_name"],
                )
            )


    session.commit()
    session.close()


def append_data(csv_name, table_name, engine):
    Session = sessionmaker(bind=engine)
    session = Session()
    dirname = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    filename = os.path.join(dirname, f"data/processed/{csv_name}")
    print(filename)
    df = pd.read_csv(filename)

    if table_name == "orders_gpt":
        for index, row in df.iterrows():
            try:
                insert_query = f"INSERT INTO {table_name} (date, hour, day_name, is_weekend, month, year, type, source, sales, count) VALUES ('{pd.to_datetime(row['date'])}', '{row['hour']}', '{row['day_name']}', '{row['is_weekend']}', '{row['month']}', '{row['year']}', '{row['type']}', '{row['source']}', '{row['sales']}', '{row['count']}') ON DUPLICATE KEY UPDATE hour = '{row['hour']}', day_name = '{row['day_name']}', is_weekend = '{row['is_weekend']}', month = '{row['month']}', year = '{row['year']}', type = '{row['type']}', source = '{row['source']}', sales = '{row['sales']}', count = '{row['count']}'"
                session.execute(insert_query)
            except Exception as e_:
                print('An error has occurred on inserting date {} - hour {} - type {} - source {} - sales {}'.format(row['date'], row['hour'], row['type'], row['source'], row['sales']))

        print("done")

    session.commit()
    session.close()



Base.metadata.create_all(data_engine)
