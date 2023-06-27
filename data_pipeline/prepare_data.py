import argparse
import os
import sys
import pandas as pd
from datetime import date, datetime, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import uuid
import hashlib
os.environ['PYTHONHASHSEED'] = '42'

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from src.helpers.utils import list_csv_files_in_directory
from src.repositories.client_repository import ClientRepository
from src.repositories.pos_repository import PosRepository
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
    # cats_to_be_deleted = df_categories[~df_categories.deleted_at.isna()]
    df_categories = df_categories[df_categories.deleted_at.isna()]
    df_categories = df_categories[["id", "client_id", category_name_col, "slug", "created_at", "updated_at", "deleted_at"]].rename(columns={category_name_col: "name"})
    df_categories.name = df_categories.name.apply(lambda x: x.capitalize())
    return df_categories

def fetch_orders(client_id, client_timezone_offset, path):
    if os.path.exists(path):
        print("Exists")
        df_orders = pd.read_csv(path)
        df_orders.reset_index(drop=True, inplace=True)
    else:
        raise Exception("File does not exist")
    
    df_orders = process_orders(df_orders, client_timezone_offset, client_id)

    return df_orders

def update_orders(client_id, client_timezone_offset, csv_files, path):
    df_orders = pd.DataFrame()
    print(csv_files)
    for file in csv_files:
        path_file = f"{path}/{file}"
        print("Preparing Path:", path_file)
        df_orders = pd.concat([df_orders, pd.read_csv(path_file)], ignore_index=True)
    print(df_orders.shape)
    print(df_orders.head())
    df_orders = process_orders(df_orders, client_timezone_offset, client_id)

    return df_orders


def process_orders(df_orders, client_timezone_offset, client_id):
    df_orders.reset_index(drop=True, inplace=True)
    df_orders.created_at = pd.to_datetime(df_orders.created_at)
    df_orders['branch'] = df_orders['branch'].astype(str)
    df_orders['branch_id'] = df_orders['branch'].apply(lambda x: eval(x)['id'])
    df_orders['client_id'] = client_id
    
    df_orders = df_orders[df_orders.status !=5] # remove the returned quantity
    df_orders = df_orders.assign(ordered_at=df_orders.created_at)
    df_orders["ordered_at"] = pd.to_datetime(df_orders["ordered_at"])
    
    time_difference = timedelta(hours=client_timezone_offset)
    print(df_orders["ordered_at"])
    df_orders["ordered_at"] += time_difference
    df_orders = df_orders[~df_orders.business_date.isna()]
    df_orders.business_date = pd.to_datetime(df_orders.business_date)
    return df_orders

def fetch_order_details(df_orders, df_products, df_categories, client_id):
    need_unavailable_category = False
    list_order_details = []
    for index, row in df_orders.iterrows():
        order_header_id = row["id"]
        # branch_id = eval(row["branch"])["id"]
        created_at = row["created_at"]
        updated_at = row["updated_at"]
        # total_price = row["total_price"]
        try:
            products = eval(row["products"])
        except:
            products = row["products"]

        for order_product in products:
            product_id = order_product["product"]["id"]
            try:
                category_id = df_products[df_products["id"] == product_id]["category_id"].values[0]
            except:
                need_unavailable_category = True
                category_id = "00000000-0000-0000-0000-000000000000"

            quantity = order_product["quantity"]
            price = order_product["total_price"]
            list_order_details.append({
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
    
    #Hash Generation
    cols=['created_at', 'header_id', 'product_id', 'quantity', 'price', 'category_id', 'client_id']
    concatenated_strings = orders_details[cols].astype(str).apply(''.join, axis=1)
    orders_details['id'] = concatenated_strings.apply(lambda x: hashlib.sha256(x.encode()).hexdigest())
    orders_details['id'] = orders_details['id'].astype(str)

    if need_unavailable_category:
        print("Yes, we need to add the unavailable category, make sure to add it ins the .env")
        new_row = pd.DataFrame({'id': '00000000-0000-0000-0000-000000000000', 'name': 'Not Available', 'slug':"not-available", 'client_id':client_id}, index=[df_categories.index.max()+1])
        df_categories = pd.concat([df_categories, new_row], ignore_index=True)
        df_categories.created_at = df_categories.created_at.fillna(datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        df_categories.updated_at = df_categories.updated_at.fillna(datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        df_categories.deleted_at = df_categories.deleted_at.fillna(method='ffill')

    return orders_details, df_categories

def fetch_order_options(df_headers, orders_details):
    list_order_options = []
    for index, row in df_headers.iterrows():
        order_header_id = row["id"]
        try:
            products = eval(row["products"])
        except:
            products = row["products"]
        for order_product in products:
            product_id = order_product["product"]["id"]
            for order_option in order_product["options"]:
                modifer_option = order_option["modifier_option"]
                name = modifer_option["name"]
                name_localized = modifer_option["name_localized"]
                sku = modifer_option["sku"]
                id = order_option["id"]
                quantity = order_option["quantity"]
                partition = order_option["partition"]
                unit_price = order_option["unit_price"]
                total_price = order_option["total_price"]
                total_cost = order_option["total_cost"]
                tax_exclusive_unit_price = order_option["tax_exclusive_unit_price"]
                tax_exclusive_total_price = order_option["tax_exclusive_total_price"]
                tax_exclusive_discount_amount = order_option["tax_exclusive_discount_amount"]
                order_details_id = orders_details[(orders_details["product_id"] == product_id) & (orders_details["header_id"] == order_header_id)]["id"].values[0]
                list_order_options.append({
                    "order_details_id": order_details_id,
                    "id": id,
                    "name": name,
                    "name_localized": name_localized,
                    "sku": sku,
                    "tax_exclusive_unit_price": tax_exclusive_unit_price,
                    "tax_exclusive_total_price": tax_exclusive_total_price,
                    "tax_exclusive_discount_amount": tax_exclusive_discount_amount,
                    "quantity": quantity,
                    "partition": partition,
                    "unit_price": unit_price,
                    "total_price": total_price,
                    "total_cost": total_cost,
                })
    df_options = pd.DataFrame(list_order_options)
    return df_options

def main():
    pd.set_option("display.max_columns", None)
    load_dotenv()

    parser = argparse.ArgumentParser()
    parser.add_argument('--client-id', type=int, required=True, help='Client ID')
    parser.add_argument('--mode', type=str, required=True, help='pull or update')
    parser.add_argument('--files', nargs='+', type=str, help='Specific file names to download or delete')


    args = parser.parse_args()

    # Get environment variables
    client_id = args.client_id
    mode = args.mode
    files = args.files

    if mode not in ['pull', 'update']:
        raise Exception('Mode must be either pull or update.')

    engine = create_engine(os.environ["DATABASE_URI"])
    session = sessionmaker(bind=engine)
    client_repo = ClientRepository(session=session())
    client = client_repo.fetch_client(client_id)
    token = client.token
    client_settings = client.settings
    client_timezone_offset = int(client_settings["client_timezone_offset"])
    category_name_col = str(client_settings["category_name_col"])

    orders_types = {1:'Dine In', 2:'Pick Up', 3:'Delivery', '4':'Drive Thru'}
    orders_sources = {1:'Cashier', 2:'API', 3:'Call Center'}
    orders_statuses = {1:'Pending', 2:'Active', 3:'Declined', 4:'Closed', 5:'Returned', 6:'Joined', 7:'Void'}

    # Fetch one-time data
    df_branches = fetch_branches(client_id, token)
    df_products = fetch_products(client_id, token, category_name_col)
    df_categories = fetch_categories(client_id, token, category_name_col)

    df_branches['opening_from'] = pd.to_datetime(df_branches['opening_from'], format='%H:%M')
    df_branches['opening_to'] = pd.to_datetime(df_branches['opening_to'], format='%H:%M')
    
    if mode == 'pull':
        if files:
            files_updated = []
            for file in files:
                base = os.path.basename(file)
                files_updated.append(base)
            del files
            csv_files = files_updated
            print(f"Files were specified: {files_updated}")

        else:
            csv_files = list_csv_files_in_directory(f'data/{client_id}/raw')
        if len(csv_files) == 0:
            raise Exception("No CSV files found.")
        
        i = 1
        for file in csv_files:
            path = f"data/{client_id}/raw/{file}"
            print("Preparing Path:", path)
            orders_header = fetch_orders(client_id, client_timezone_offset, path)
            orders_details, df_categories = fetch_order_details(orders_header, df_products, df_categories, client_id)
            df_options = fetch_order_options(orders_header, orders_details)

            # Perform additional processing...
            print(orders_header.shape)
            print(orders_details.shape)
            print(df_options.shape)
            
            orders_header['type'] = orders_header['type'].map(orders_types)
            orders_header['source'] = orders_header['source'].map(orders_sources)
            orders_header['status'] = orders_header['status'].map(orders_statuses)
            orders_header['ordered_at'] = pd.to_datetime(orders_header['ordered_at']).dt.time
            orders_header['status'].fillna('Void', inplace=True)
            orders_header['business_date'] = pd.to_datetime(orders_header['business_date'], format="%Y-%m-%d")
            df_options['name_localized'].fillna('-', inplace=True)


            orders_header.drop_duplicates(subset=['id'], inplace=True)
            df_options.drop_duplicates(subset=['id'], inplace=True)
            orders_details.drop_duplicates(subset=['id'], inplace=True)

            #orders_header = orders_header[["id", 'products', "client_id", "branch_id", "source", "type", "status", 'discount_amount', "total_price", 'subtotal_price', 'business_date', "created_at", "updated_at"]]

            df_categories.to_csv(f"data/{client_id}/processed/categories.csv", index=False)
            df_branches.to_csv(f"data/{client_id}/processed/branches.csv", index=False)
            df_products.to_csv(f"data/{client_id}/processed/products.csv", index=False)
            orders_details.to_csv(f"data/{client_id}/processed/order_details_{i}.csv", index=False)
            orders_header.to_csv(f"data/{client_id}/processed/order_headers_{i}.csv", index=False)
            df_options.to_csv(f"data/{client_id}/processed/order_options_{i}.csv", index=False)
            i += 1

            print("Finished preparing Path:", path)
            print("====================================")
    
    elif mode == 'update':
        path = f'data/{client_id}/raw/updates'
        csv_files = list_csv_files_in_directory(path)
        orders_header = update_orders(client_id, client_timezone_offset, csv_files, path)
        orders_details, df_categories = fetch_order_details(orders_header, df_products,df_categories, client_id)
        df_options = fetch_order_options(orders_header, orders_details)

        # Perform additional processing...

        orders_header['type'] = orders_header['type'].map(orders_types)
        orders_header['source'] = orders_header['source'].map(orders_sources)
        orders_header['status'] = orders_header['status'].map(orders_statuses)
        orders_header['ordered_at'] = pd.to_datetime(orders_header['ordered_at']).dt.time
        orders_header['status'].fillna('Void', inplace=True)
        orders_header['business_date'] = pd.to_datetime(orders_header['business_date'], format="%Y-%m-%d")

        #check size of df_options
        if df_options.shape[0] > 0:
            df_options['name_localized'].fillna('-', inplace=True)

        orders_header.drop_duplicates(subset=['id'], inplace=True)
        df_options.drop_duplicates(subset=['id'], inplace=True)
        orders_details.drop_duplicates(subset=['id'], inplace=True)

        #orders_header = orders_header[["id", 'products', "client_id", "branch_id", "source", "type", "status", 'discount_amount', "total_price", 'subtotal_price', 'business_date', "created_at", "updated_at"]]


        df_categories.to_csv(f"data/{client_id}/processed/updates/categories.csv", index=False)
        df_branches.to_csv(f"data/{client_id}/processed/updates/branches.csv", index=False)
        df_products.to_csv(f"data/{client_id}/processed/updates/products.csv", index=False)
        
        orders_details.to_csv(f"data/{client_id}/processed/updates/order_details.csv", index=False)
        orders_header.to_csv(f"data/{client_id}/processed/updates/order_headers.csv", index=False)
        df_options.to_csv(f"data/{client_id}/processed/updates/order_options.csv", index=False)

        print("Finished preparing Path:", path)
        print("====================================")

if __name__ == "__main__":
    main()
