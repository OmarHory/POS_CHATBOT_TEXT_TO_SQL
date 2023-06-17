import argparse
import os
import sys
import pandas as pd
from datetime import date, datetime, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import uuid
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from src.repositories.client_repository import ClientRepository
from utils import call_foodics, generate_slug
from dotenv import load_dotenv

def fetch_branches(client_id, token):
    last_page = call_foodics("branches", 1, client_id, token, return_last_page=True)
    list_responses = call_foodics("branches", last_page, client_id, token)
    df_branches = pd.DataFrame([item for sublist in list_responses for item in sublist])
    df_branches["client_id"] = client_id
    df_branches["slug"] = df_branches.name.apply(lambda x: generate_slug(x))
    df_branches = df_branches[["id", "client_id", "name", "slug", "opening_from", "opening_to", "created_at", "updated_at", "deleted_at"]]
    return df_branches

def fetch_products(client_id, token, category_name_col):
    last_page = call_foodics("products", 1, client_id, token, return_last_page=True)
    list_responses = call_foodics("products", last_page, client_id, token, includables="category")
    df_products = pd.DataFrame([item for sublist in list_responses for item in sublist])
    df_products["client_id"] = client_id
    df_products["slug"] = df_products.name.apply(lambda x: generate_slug(x))
    df_products["category_name"] = df_products["category"].apply(lambda x: x[category_name_col])
    df_products = df_products[~df_products.category_name.isna()]
    df_products["category_name"] = df_products["category_name"].apply(lambda x: x.capitalize())
    df_products["category_id"] = df_products["category"].apply(lambda x: x["id"])
    df_products.rename(columns={"sku": "sku"}, inplace=True)
    df_products.drop("category", axis=1, inplace=True)
    df_products = df_products[["id", "client_id", "sku", "slug", "name", "category_id", "is_active", "is_stock_product", "price", "created_at", "updated_at", "deleted_at"]]
    df_products = df_products.rename(columns={"is_stock_product": "is_stock"})
    return df_products

def fetch_categories(client_id, token, category_name_col):
    last_page = call_foodics("categories", 1, client_id, token, return_last_page=True)
    list_responses = call_foodics("categories", last_page, client_id, token)
    df_categories = pd.DataFrame([item for sublist in list_responses for item in sublist])
    df_categories["client_id"] = client_id
    df_categories["slug"] = df_categories.name.apply(lambda x: generate_slug(x))
    cats_to_be_deleted = df_categories[~df_categories.deleted_at.isna()]
    df_categories = df_categories[df_categories.deleted_at.isna()]
    df_categories = df_categories[["id", "client_id", category_name_col, "slug", "created_at", "updated_at", "deleted_at"]].rename(columns={category_name_col: "name"})
    df_categories.name = df_categories.name.apply(lambda x: x.capitalize())
    return df_categories

def fetch_orders(client_id, token, client_timezone_offset):
    filter = {}
    path = f"data/{client_id}/raw/orders.csv"
    if os.path.exists(path):
        df_orders = pd.read_csv(path)
        df_orders.reset_index(drop=True, inplace=True)
    else:
        includables = "branch,products.product,products.options.modifier_option"
        last_page = call_foodics("orders", 1, client_id, token, includables=includables, filter=filter, return_last_page=True)
        last_page = 5
        list_responses = call_foodics("orders", last_page, client_id, token, includables=includables, filter=filter, do_checkpoint=False)
        df_orders = pd.DataFrame([item for sublist in list_responses for item in sublist])
        df_orders.to_csv(path, index=False)
    df_orders = pd.read_csv(path)
    df_orders.reset_index(drop=True, inplace=True)
    df_orders.created_at = pd.to_datetime(df_orders.created_at)
    df_orders['branch'] = df_orders['branch'].astype(str)
    df_orders['branch_id'] = df_orders['branch'].apply(lambda x: eval(x)['id'])
    df_orders['client_id'] = client_id
    
    orders_header = df_orders[["id", "client_id", "branch_id", "source", "type", "status", "total_price", "created_at", "updated_at"]]
    orders_header = orders_header.assign(ordered_at=orders_header.created_at)
    orders_header["ordered_at"] = pd.to_datetime(orders_header["ordered_at"])
    time_difference = timedelta(hours=client_timezone_offset)
    orders_header["ordered_at"] += time_difference

    return df_orders, orders_header

def fetch_order_details(df_orders,df_products, client_id):
    list_order_details = []
    for index, row in df_orders.iterrows():
        order_header_id = row["id"]
        branch_id = eval(row["branch"])["id"]
        created_at = row["created_at"]
        updated_at = row["updated_at"]
        total_price = row["total_price"]
        for order_product in eval(row["products"]):
            order_details_id = str(uuid.uuid4())
            product_id = order_product["product"]["id"]
            try:
                category_id = df_products[df_products["id"] == product_id]["category_id"].values[0]
            except:
                category_id = "00000000-0000-0000-0000-000000000000"
            quantity = order_product["quantity"]
            price = order_product["total_price"]
            list_order_details.append({
                "id": order_details_id,
                "header_id": order_header_id,
                "product_id": product_id,
                "category_id": category_id,
                "client_id": client_id,
                "quantity": quantity,
                "price": price,
                "created_at": created_at,
                "updated_at": updated_at,
            })
    orders_details = pd.DataFrame(list_order_details)
    return orders_details

def fetch_order_options(df_orders, orders_details):
    df_options = pd.DataFrame(eval(df_orders.head()["products"][0])[0]["options"])
    list_order_options = []
    for index, row in df_orders.iterrows():
        order_header_id = row["id"]
        for order_product in eval(row["products"]):
            product_id = order_product["product"]["id"]
            for order_option in order_product["options"]:
                modifer_option = order_option["modifier_option"]
                option_name = modifer_option["name"]
                option_name_localized = modifer_option["name_localized"]
                option_sku = modifer_option["sku"]
                option_id = order_option["id"]
                option_quantity = order_option["quantity"]
                option_partition = order_option["partition"]
                option_unit_price = order_option["unit_price"]
                option_total_price = order_option["total_price"]
                option_total_cost = order_option["total_cost"]
                order_details_id = orders_details[(orders_details["product_id"] == product_id) & (orders_details["header_id"] == order_header_id)]["id"].values[0]
                list_order_options.append({
                    "order_details_id": order_details_id,
                    "option_id": option_id,
                    "option_name": option_name,
                    "option_name_localized": option_name_localized,
                    "option_sku": option_sku,
                    "option_quantity": option_quantity,
                    "option_partition": option_partition,
                    "option_unit_price": option_unit_price,
                    "option_total_price": option_total_price,
                    "option_total_cost": option_total_cost,
                })
    df_options = pd.DataFrame(list_order_options)
    return df_options

def main():
    pd.set_option("display.max_columns", None)
    load_dotenv()

    parser = argparse.ArgumentParser()
    parser.add_argument('--client-id', type=int, required=True, help='Client ID')
    args = parser.parse_args()

    # Get environment variables
    client_id = args.client_id

    engine = create_engine(os.environ["DATABASE_URI"])
    session = sessionmaker(bind=engine)
    client_repo = ClientRepository(session=session())
    client = client_repo.fetch_client(client_id)
    token = client.token
    client_settings = client.settings
    client_timezone_offset = int(client_settings["client_timezone_offset"])
    category_name_col = str(client_settings["category_name_col"])

    df_branches = fetch_branches(client_id, token)
    df_products = fetch_products(client_id, token, category_name_col)
    df_categories = fetch_categories(client_id, token, category_name_col)
    df_orders, orders_header = fetch_orders(client_id, token, client_timezone_offset)
    orders_details = fetch_order_details(df_orders, df_products, client_id)
    df_options = fetch_order_options(df_orders, orders_details)

    df_products.to_csv(f"data/{client_id}/raw/products.csv", index=False)
    orders_details.to_csv(f"data/{client_id}/raw/order_details.csv", index=False)
    orders_header.to_csv(f"data/{client_id}/raw/order_header.csv", index=False)
    df_categories.to_csv(f"data/{client_id}/raw/categories.csv", index=False)
    df_branches.to_csv(f"data/{client_id}/raw/branches.csv", index=False)
    df_options.to_csv(f"data/{client_id}/raw/options.csv", index=False)

    df_products.head()
    orders_details.head()
    orders_header.head()
    df_branches.head()
    df_categories.head()
    df_options.head()

if __name__ == "__main__":
    main()
