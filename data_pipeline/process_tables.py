import argparse
import os
import pandas as pd
from dotenv import load_dotenv
from utils import generate_slug

def preprocess_data(client_id):
    # Read all data
    raw_data_path = f'data/{client_id}/raw/'
    processed_data_path = f'data/{client_id}/processed/'

    orders_header = pd.read_csv(os.path.join(raw_data_path, 'order_header.csv'))
    orders_details = pd.read_csv(os.path.join(raw_data_path, 'order_details.csv'))
    products = pd.read_csv(os.path.join(raw_data_path, 'products.csv'))
    branches = pd.read_csv(os.path.join(raw_data_path, 'branches.csv'))
    categories = pd.read_csv(os.path.join(raw_data_path, 'categories.csv'))
    options = pd.read_csv(os.path.join(raw_data_path, 'options.csv'))

    # Orders Headers
    orders_types = {1: 'Dine In', 2: 'Pick Up', 3: 'Delivery', '4': 'Drive Thru'}
    orders_sources = {1: 'Cashier', 2: 'API', 3: 'Call Center'}
    orders_statuses = {1: 'Pending', 2: 'Active', 3: 'Declined', 4: 'Closed', 5: 'Returned', 6: 'Joined', 7: 'Void'}

    orders_header['type'] = orders_header['type'].map(orders_types)
    orders_header['source'] = orders_header['source'].map(orders_sources)
    orders_header['status'] = orders_header['status'].map(orders_statuses)

    orders_header['ordered_at'] = pd.to_datetime(orders_header['ordered_at'])

    orders_header.drop_duplicates(inplace=True)
    orders_header['status'].fillna('Void', inplace=True)

    # Products
    products['slug'] = products.name.apply(lambda x: generate_slug(x))

    # Branches
    branches['opening_from'] = pd.to_datetime(branches['opening_from'])
    branches['opening_to'] = pd.to_datetime(branches['opening_to'])

    # Order Options (Modifiers)
    options['option_name_localized'].fillna('-', inplace=True)

    # Write processed data
    processed_data_path = f'data/{client_id}/processed/'
    os.makedirs(processed_data_path, exist_ok=True)

    orders_header.to_csv(os.path.join(processed_data_path, 'order_header.csv'), index=False)
    orders_details.to_csv(os.path.join(processed_data_path, 'order_details.csv'), index=False)
    products.to_csv(os.path.join(processed_data_path, 'products.csv'), index=False)
    branches.to_csv(os.path.join(processed_data_path, 'branches.csv'), index=False)
    categories.to_csv(os.path.join(processed_data_path, 'categories.csv'), index=False)
    options.to_csv(os.path.join(processed_data_path, 'options.csv'), index=False)

    print("Data preprocessing completed successfully.")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Data preprocessing script')
    parser.add_argument('--client-id', type=int, help='Client ID')

    args = parser.parse_args()
    preprocess_data(args.client_id)
