from abc import ABC, abstractmethod
from sqlalchemy import create_engine, func, and_
from sqlalchemy import exists
from sqlalchemy.orm import sessionmaker
import pandas as pd
import os, sys

#import models from models/models.py
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(parent_dir)
from models.models import OrderHeader, OrderDetail, Branch, Category, Product, Client, OrderOption

class PosRepository:
    def __init__(self, db_uri):
        self.engine = create_engine(db_uri)
        Session = sessionmaker(bind=self.engine)
        self.session = Session()

    def close_session(self):
        self.session.close()
    
    def insert_data(self, client_id, csv_name, table_name, path):
        dirname = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        filename = os.path.join(dirname, f"{path}/{csv_name}")
        print(filename)
        ##query Client where slug = blk
        client = self.session.query(Client).filter(Client.id == client_id).first()

        if not client:
            print("Client {} not found.".format(client_id))
            return

        try:
            df = pd.read_csv(filename)
        except pd.errors.EmptyDataError:
            print("File {} is empty.".format(filename))
            return

        for _, row in df.iterrows():
            model = self.get_model(table_name)
            # check if record exists (use exists() method)

            col = "id"
            record_exists = self.session.query(exists().where(model.external_id == row[col])).scalar()

            if record_exists:
                print("Record {} already exists.".format(row[col]))
                pass
            else:
                if table_name == "branches":
                    obj = Branch(
                            external_id=row["id"],
                            name=row["name"],
                            slug=row["slug"],
                            client_id=client_id,
                            opening_from=pd.to_datetime(row["opening_from"]),
                            opening_to=pd.to_datetime(row["opening_to"]),
                            created_at=pd.to_datetime(row["created_at"]),
                            updated_at=pd.to_datetime(row["updated_at"]),
                        )
                elif table_name == "categories":
                    obj = Category(
                            external_id=row["id"],
                            name=row["name"],
                            slug=row["slug"],
                            client_id=client_id,
                            created_at=pd.to_datetime(row["created_at"]),
                            updated_at=pd.to_datetime(row["updated_at"]),
                        )
                elif table_name == "products":
                    obj = Product(
                            external_id=row["id"],
                            name=row["name"],
                            sku=row["sku"],
                            category_id=self.query_record_by_uuid(table_name="categories", external_id=row["category_id"]),
                            is_active=row["is_active"],
                            is_stock=row["is_stock"],
                            price=row["price"],
                            client_id=client_id,
                            created_at=pd.to_datetime(row["created_at"]),
                            updated_at=pd.to_datetime(row["updated_at"]),
                        )
                elif table_name == "order_headers":
                    obj = OrderHeader(
                            external_id=row["id"],
                            branch_id=self.query_record_by_uuid(table_name='branches', external_id=row["branch_id"]),
                            order_date=pd.to_datetime(row["business_date"], format="%Y-%m-%d"),
                            order_time=pd.to_datetime(row["ordered_at"]),
                            type=row["type"],
                            source=row["source"],
                            status=row["status"],
                            total_price=row["total_price"],
                            discount_amount=row["discount_amount"],
                            client_id=client_id,
                            created_at=pd.to_datetime(row["created_at"]),
                            updated_at=pd.to_datetime(row["updated_at"]),
                        )
                elif table_name == "order_details":
                    obj = OrderDetail(
                            external_id=row["id"],
                            order_header_id=self.query_record_by_uuid(table_name='order_headers', external_id=row["header_id"]),
                            product_id=self.query_record_by_uuid(table_name='products', external_id = row["product_id"]),
                            quantity=row["quantity"],
                            price=row["price"],
                            client_id=client_id,
                            created_at=pd.to_datetime(row["created_at"]),
                            updated_at=pd.to_datetime(row["updated_at"]),
                        )
                elif table_name == "order_options":
                    od_id = self.query_record_by_uuid(table_name='order_details', external_id=row["order_details_id"])
                    # if not od_id:
                    #     continue
                    obj = OrderOption(
                            external_id=row["id"],
                            order_details_id=od_id,
                            name=row["name"],
                            name_localized=row["name_localized"],
                            sku=row["sku"],
                            tax_exclusive_unit_price = row["tax_exclusive_unit_price"],
                            tax_exclusive_total_price = row["tax_exclusive_total_price"],
                            tax_exclusive_discount_amount = row["tax_exclusive_discount_amount"],
                            quantity=row["quantity"],
                            unit_price=row["unit_price"],
                            price=row["total_price"],
                            cost=row["total_cost"],
                            client_id=client_id,
                        )
                else:
                    print("Table name not found.")
                    return

                self.insert_record(obj)


    def query_record_by_uuid(self, table_name, external_id):
        model = self.get_model(table_name)
        record = self.session.query(model).filter_by(external_id=external_id).first();
        self.session.close()
        return record.id if record else None
    

    def get_max_order_date(self, client_id):
        max_date = self.session.query(func.max(OrderHeader.order_date)).filter_by(client_id=client_id).scalar()
        return max_date


    def get_model(self, table_name):
        if table_name == "clients":
            return Client
        if table_name == "order_headers":
            return OrderHeader
        if table_name == "order_details":
            return OrderDetail
        if table_name == "branches":
            return Branch
        if table_name == "products":
            return Product
        if table_name == "categories":
            return Category
        if table_name == "order_options":
            return OrderOption
    
    def insert_record(self, model_obj):
        self.session.add(model_obj)
        self.session.commit()

    def execute_query(self, query):
        try:
            result = self.session.execute(query)
            # Fetch all the rows from the result of query
            rows = result.fetchall()
            # Return the rows
            return rows
        except Exception as e:
            print("Failed to execute query.")
            print("Error: ", e)
            self.session.rollback()
            return None
        finally:
            self.session.close()

    def dd(self, obj):
        print(obj)
        sys.exit(1)  # Terminate the program