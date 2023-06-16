import datetime
from sqlalchemy import (
    Index,
    create_engine,
    Column,
    Integer,
    String,
    Float,
    Date,
    Boolean,
    DateTime,
    ForeignKey,
    Time,
    Text,
    JSON,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import relationship


Base = declarative_base()


class Client(Base):
    __tablename__ = "clients"

    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    slug = Column(String(255))
    settings = Column(JSON)
    token = Column(Text)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)
    deleted_at = Column(DateTime, nullable=True)


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    email = Column(String(255), nullable=True)
    phone_number = Column(String(255))
    created_at = Column(DateTime)
    updated_at = Column(DateTime)
    deleted_at = Column(DateTime, nullable=True)


class ClientUser(Base):
    __tablename__ = "client_user"

    user_id = Column(Integer, ForeignKey("users.id"), primary_key=True)
    client_id = Column(Integer, ForeignKey("clients.id"), primary_key=True)
    created_at = Column(DateTime)

    user = relationship("User")
    client = relationship("Client")


class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, autoincrement=True)
    external_id = Column(String(255), nullable=False)
    name = Column(String(255), nullable=False)
    slug = Column(String(255))
    client_id = Column(Integer, ForeignKey("clients.id"))
    created_at = Column(DateTime)
    updated_at = Column(DateTime)
    deleted_at = Column(DateTime, nullable=True)

    client = relationship("Client")

    __table_args__ = (Index("idx_external_id", external_id, unique=True),)


class Branch(Base):
    __tablename__ = "branches"

    id = Column(Integer, primary_key=True, autoincrement=True)
    external_id = Column(String(255), nullable=False)
    name = Column(String(255), nullable=False)
    slug = Column(String(255), nullable=False)
    client_id = Column(Integer, ForeignKey("clients.id"), nullable=False)
    opening_from = Column(DateTime)
    opening_to = Column(DateTime)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)
    deleted_at = Column(DateTime)

    client = relationship("Client")

    __table_args__ = (Index("idx_external_id", external_id, unique=True),)


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, autoincrement=True)
    external_id = Column(String(255), nullable=False)
    name = Column(String(255), nullable=False)
    sku = Column(String(255))
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=True)
    is_active = Column(Boolean)
    is_stock = Column(Boolean)
    price = Column(Float(precision=2))
    client_id = Column(Integer, ForeignKey("clients.id"), nullable=False)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)
    deleted_at = Column(DateTime)

    category = relationship("Category")
    client = relationship("Client")

    __table_args__ = (Index("idx_external_id", external_id, unique=True),)


class OrderHeader(Base):
    __tablename__ = "order_headers"

    id = Column(Integer, primary_key=True, autoincrement=True)
    external_id = Column(String(255), nullable=False)
    branch_id = Column(Integer, ForeignKey("branches.id"), nullable=False)
    type = Column(String(255))
    source = Column(String(255))
    status = Column(String(255))
    total_price = Column(Float(precision=2))
    client_id = Column(Integer, ForeignKey("clients.id"), nullable=False)
    ordered_at = Column(DateTime)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)

    branch = relationship("Branch")
    client = relationship("Client")

    __table_args__ = (Index("idx_external_id", external_id, unique=True),)


class OrderDetail(Base):
    __tablename__ = "order_details"

    id = Column(Integer, primary_key=True, autoincrement=True)
    external_id = Column(String(255), nullable=False)
    order_header_id = Column(Integer, ForeignKey("order_headers.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    quantity = Column(Integer)
    price = Column(Float(precision=2))
    client_id = Column(Integer, ForeignKey("clients.id"), nullable=False)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)

    header = relationship("OrderHeader")
    product = relationship("Product")
    client = relationship("Client")

    __table_args__ = (Index("idx_external_id", external_id, unique=True),)


class OrderOption(Base):
    __tablename__ = "order_options"

    id = Column(Integer, primary_key=True, autoincrement=True)
    external_id = Column(String(255), nullable=False)
    order_details_id = Column(Integer, ForeignKey("order_details.id"), nullable=False)
    name = Column(String(255))
    name_localized = Column(String(255))
    sku = Column(String(255))
    client_id = Column(Integer, ForeignKey("clients.id"), nullable=False)
    quantity = Column(Integer)
    unit_price = Column(Float(precision=2))
    total_price = Column(Float(precision=2))
    total_cost = Column(Float(precision=2))

    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow)

    detail = relationship("OrderDetail")
    client = relationship("Client")

    __table_args__ = (Index("idx_external_id", external_id, unique=True),)


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
    input_type = Column(String(255))
    client_id = Column(Integer, ForeignKey("clients.id"))
    created_at = Column(DateTime)

    client = relationship("Client")

    def __repr__(self):
        return f"<MessageLog {self.id}: {self.phone_number} - {self.message_type} - {self.timestamp}>"
