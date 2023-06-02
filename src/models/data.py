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
    order_datetime = Column(DateTime(timezone=True))
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
    price = Column(Float(precision=2))

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
                    order_datetime=pd.to_datetime(row["order_datetime"]),
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
                    price=row["price"],
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


def update_data(csv_name, table_name, engine):
    Session = sessionmaker(bind=engine)
    session = Session()
    dirname = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    filename = os.path.join(dirname, f"data/processed/updates/{csv_name}")
    print(filename)
    df = pd.read_csv(filename)

    if table_name == "order_header":
        for index, row in df.iterrows():
            record = session.query(OrderHeader).filter_by(order_header_id=row["order_header_id"]).first()
            if record:
                record.branch_id = row["branch_id"]
                record.order_datetime = pd.to_datetime(row["order_datetime"])
                record.order_type = row["order_type"]
                record.order_source = row["order_source"]
                record.order_status = row["order_status"]
                record.order_total_price = row["order_total_price"]
                session.merge(record)
            else:
                session.add(
                    OrderHeader(
                        order_header_id=row["order_header_id"],
                        branch_id=row["branch_id"],
                        order_datetime=pd.to_datetime(row["order_datetime"]),
                        order_type=row["order_type"],
                        order_source=row["order_source"],
                        order_status=row["order_status"],
                        order_total_price=row["order_total_price"],
                    )
                )

    if table_name == "order_details":
        for index, row in df.iterrows():
            record = session.query(OrderDetails).filter_by(order_details_id=row["order_details_id"]).first()
            if record:
                record.order_header_id = row["order_header_id"]
                record.product_id = row["product_id"]
                record.category_id = row["category_id"]
                record.quantity = row["quantity"]
                record.price = row["price"]  
                session.merge(record)
            else:
                session.add(
                    OrderDetails(
                        order_details_id=row["order_details_id"],
                        order_header_id=row["order_header_id"],
                        product_id=row["product_id"],
                        category_id=row["category_id"],
                        quantity=row["quantity"],
                        price=row["price"],  
                    )
                )


    if table_name == "branches":
        for index, row in df.iterrows():
            record = session.query(Branches).filter_by(branch_id=row["branch_id"]).first()
            if record:
                record.branch_name = row["branch_name"]
                record.opening_from = row["opening_from"]
                record.opening_to = row["opening_to"]
                session.merge(record)
            else:
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
            record = session.query(Products).filter_by(product_id=row["product_id"]).first()
            if record:
                record.product_name = row["product_name"]
                record.product_sku = row["product_sku"]
                record.category_id = row["category_id"]
                record.category_name = row["category_name"]
                record.is_active = row["is_active"]
                record.is_stock_product = row["is_stock_product"]
                record.price = row["price"]
                session.merge(record)
            else:
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
            record = session.query(Categories).filter_by(category_id=row["category_id"]).first()
            if record:
                record.category_name = row["category_name"]
                session.merge(record)
            else:
                session.add(
                    Categories(
                        category_id=row["category_id"],
                        category_name=row["category_name"],
                    )
                )

    session.commit()
    session.close()





Base.metadata.create_all(data_engine)
