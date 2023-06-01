import boto3
from src.config import config_aws
import argparse

parser = argparse.ArgumentParser(description='Process method argument')

parser.add_argument('method', choices=['download', 'upload'], help='Specify the method: download or upload')

args = parser.parse_args()

method = args.method

s3 = boto3.client('s3', aws_access_key_id=config_aws['access_key'], aws_secret_access_key=config_aws['secret_access_key'])
bucket_name = config_aws['bucket_name']

if method == 'download':
    print('Performing download...')

    for name in ['orders_final_include.csv']:
        s3.download_file(bucket_name, f'chicks/{name}', f'data/{name}')
elif method == 'upload':
    print('Performing upload...')
    for name in ['orders_final_include_updated.csv']:
        s3.upload_file(f'data/{name}', bucket_name, f'chicks/orders_final_include.csv')

else:
    raise ValueError('Invalid method specified')
