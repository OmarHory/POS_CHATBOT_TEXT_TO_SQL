from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import pandas as pd
import os, sys

#import models from models/models.py
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(parent_dir)
from models.models import OrderHeader, OrderDetail, Branch, Category, Product, Client

class PosRepository:
    def __init__(self, db_uri):
        self.engine = create_engine(db_uri)
        Session = sessionmaker(bind=self.engine)
        self.session = Session()

    def close_session(self):
        self.session.close()
    
    def insert_data(self, client_id, csv_name, table_name):
        dirname = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        filename = os.path.join(dirname, f"data/{client_id}/processed/{csv_name}")
        print(filename)
        ##query Client where slug = blk
        client = self.session.query(Client).filter(Client.id == client_id).first()

        if not client:
            print("Client {} not found.".format(client_id))
            return


        df = pd.read_csv(filename)

        if table_name == "order_headers":
            for index, row in df.iterrows():
                self.session.add(
                    OrderHeader(
                        id=row["id"],
                        branch_id=row["branch_id"],
                        ordered_at=pd.to_datetime(row["ordered_at"]),
                        type=row["type"],
                        source=row["source"],
                        status=row["status"],
                        total_price=row["total_price"],
                        client_id=client_id,
                        created_at=pd.to_datetime(row["created_at"]),
                        updated_at=pd.to_datetime(row["updated_at"]),
                    )
                )
        
        if table_name == "order_details":
            for index, row in df.iterrows():
                self.session.add(
                    OrderDetail(
                        id=row["id"],
                        header_id=row["header_id"],
                        product_id=row["product_id"],
                        quantity=row["quantity"],
                        price=row["price"],
                        client_id=client_id,
                        created_at=pd.to_datetime(row["created_at"]),
                        updated_at=pd.to_datetime(row["updated_at"]),
                    )
                )

        if table_name == "branches":
            for index, row in df.iterrows():
                self.session.add(
                    Branch(
                        id=row["id"],
                        name=row["name"],
                        slug=row["slug"],
                        client_id=client_id,
                        opening_from=pd.to_datetime(row["opening_from"]),
                        opening_to=pd.to_datetime(row["opening_to"]),
                        created_at=pd.to_datetime(row["created_at"]),
                        updated_at=pd.to_datetime(row["updated_at"]),
                        deleted_at=pd.to_datetime(row["deleted_at"]),
                    )
                )
        
        if table_name == "products":
            for index, row in df.iterrows():
                self.session.add(
                    Product(
                        id=row["id"],
                        name=row["name"],
                        sku=row["sku"],
                        category_id=row["category_id"],
                        is_active=row["is_active"],
                        is_stock=row["is_stock"],
                        price=row["price"],
                        client_id=client_id,
                        created_at=pd.to_datetime(row["created_at"]),
                        updated_at=pd.to_datetime(row["updated_at"]),
                        deleted_at=pd.to_datetime(row["deleted_at"]),
                    )
                )

        if table_name == "categories":

            for index, row in df.iterrows():
                self.session.add(
                    Category(
                        id=row["id"],
                        name=row["name"],
                        slug=row["slug"],
                        client_id=client_id,
                        created_at=pd.to_datetime(row["created_at"]),
                        updated_at=pd.to_datetime(row["updated_at"]),
                        deleted_at=pd.to_datetime(row["deleted_at"]),
                    )
                )

        self.session.commit()

    def update_data(self, client_id, csv_name, table_name):
        dirname = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        filename = os.path.join(dirname, f"data/processed/updates/{csv_name}")
        print(filename)
        df = pd.read_csv(filename)

        ##query Client where slug = blk
        client = self.session.query(Client).filter(Client.id == client_id).first()

        if not client:
            print("Client {} not found.".format(client_id))
            return

        if table_name == "order_headers":
            for index, row in df.iterrows():
                record = self.session.query(OrderHeader).filter_by(id=row["id"]).first()
                if record:
                    record.branch_id = row["branch_id"]
                    record.ordered_at = pd.to_datetime(row["ordered_at"])
                    record.type = row["type"]
                    record.source = row["source"]
                    record.status = row["status"]
                    record.total_price = row["total_price"]
                    record.client_id = client_id
                    record.created_at = pd.to_datetime(row["created_at"])
                    record.updated_at = pd.to_datetime(row["updated_at"])
                    self.session.merge(record)
                else:
                    self.session.add(
                        OrderHeader(
                            id=row["id"],
                            branch_id=row["branch_id"],
                            ordered_at=pd.to_datetime(row["ordered_at"]),
                            type=row["type"],
                            source=row["source"],
                            status=row["status"],
                            total_price=row["total_price"],
                            client_id=client_id,
                            created_at=pd.to_datetime(row["created_at"]),
                            updated_at=pd.to_datetime(row["updated_at"]),
                        )
                    )

        if table_name == "order_details":
            for index, row in df.iterrows():
                record = self.session.query(OrderDetail).filter_by(id=row["id"]).first()
                if record:
                    record.header_id = row["header_id"]
                    record.product_id = row["product_id"]
                    record.quantity=row["quantity"],
                    record.price = row["price"]
                    record.client_id = client_id
                    record.created_at = pd.to_datetime(row["created_at"])
                    record.updated_at = pd.to_datetime(row["updated_at"])
                    self.session.merge(record)
                else:
                    self.session.add(
                        OrderDetail(
                            id=row["id"],
                            header_id=row["header_id"],
                            product_id=row["product_id"],
                            quantity=row["quantity"],
                            price=row["price"],
                            client_id=client_id,
                            created_at=pd.to_datetime(row["created_at"]),
                            updated_at=pd.to_datetime(row["updated_at"]),
                        )
                    )


        if table_name == "branches":
            for index, row in df.iterrows():
                record = self.session.query(Branch).filter_by(id=row["id"]).first()
                if record:
                    record.name = row["name"]
                    record.slug = row["slug"]
                    record.client_id = client_id
                    record.opening_from = pd.to_datetime(row["opening_from"])
                    record.opening_to = pd.to_datetime(row["opening_to"])
                    record.created_at = pd.to_datetime(row["created_at"])
                    record.updated_at = pd.to_datetime(row["updated_at"])
                    record.deleted_at = pd.to_datetime(row["deleted_at"])
                    self.session.merge(record)
                else:
                    self.session.add(
                        Branch(
                            id=row["id"],
                            name=row["name"],
                            slug=row["slug"],
                            client_id=client_id,
                            opening_from=pd.to_datetime(row["opening_from"]),
                            opening_to=pd.to_datetime(row["opening_to"]),
                            created_at=pd.to_datetime(row["created_at"]),
                            updated_at=pd.to_datetime(row["updated_at"]),
                            deleted_at=pd.to_datetime(row["deleted_at"]),
                        )
                    )

        if table_name == "products":
            for index, row in df.iterrows():
                record = self.session.query(Product).filter_by(id=row["id"]).first()
                if record:
                    record.name = row["name"]
                    record.sku = row["sku"]
                    record.category_id = row["category_id"]
                    record.is_active = row["is_active"]
                    record.is_stock = row["is_stock"]
                    record.price = row["price"]
                    record.client_id = client_id
                    record.created_at = pd.to_datetime(row["created_at"])
                    record.updated_at = pd.to_datetime(row["updated_at"])
                    record.deleted_at = pd.to_datetime(row["deleted_at"])
                    self.session.merge(record)
                else:
                    self.session.add(
                        Product(
                            id=row["id"],
                            name=row["name"],
                            sku=row["sku"],
                            category_id=row["category_id"],
                            is_active=row["is_active"],
                            is_stock=row["is_stock"],
                            price=row["price"],
                            client_id=client_id,
                            created_at=pd.to_datetime(row["created_at"]),
                            updated_at=pd.to_datetime(row["updated_at"]),
                            deleted_at=pd.to_datetime(row["deleted_at"]),
                        )
                    )

        if table_name == "categories":
            for index, row in df.iterrows():
                record = self.session.query(Category).filter_by(id=row["id"]).first()
                if record:
                    record.name = row["name"]
                    record.slug = row["slug"]
                    record.client_id = client_id
                    record.created_at = pd.to_datetime(row["created_at"])
                    record.updated_at = pd.to_datetime(row["updated_at"])
                    record.deleted_at = pd.to_datetime(row["deleted_at"])
                    self.session.merge(record)
                else:
                    self.session.add(
                        Category(
                            id=row["id"],
                            name=row["name"],
                            slug=row["slug"],
                            client_id=client_id,
                            created_at=pd.to_datetime(row["created_at"]),
                            updated_at=pd.to_datetime(row["updated_at"]),
                            deleted_at=pd.to_datetime(row["deleted_at"]),
                        )
                    )

        self.session.commit()
        self.session.close()