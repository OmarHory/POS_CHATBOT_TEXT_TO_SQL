##

import os, sys

parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(parent_dir)
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
sys.path.append(parent_dir)
##
import update_variables

from models.data import *

Base.metadata.drop_all(data_engine)
Base.metadata.create_all(data_engine)


insert_data("branches.csv", "branches", data_engine)
insert_data("categories.csv", "categories", data_engine)
insert_data("products.csv", "products", data_engine)
insert_data("order_header.csv", "order_header", data_engine)
insert_data("order_details.csv", "order_details", data_engine)




data_engine.dispose()
