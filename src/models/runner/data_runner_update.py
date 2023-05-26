##
import os, sys

parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(parent_dir)
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
sys.path.append(parent_dir)
##

from models.data import *

Base.metadata.drop_all(data_engine)
Base.metadata.create_all(data_engine)

append_data("orders_updated.csv", "orders_gpt", data_engine)


data_engine.dispose()
