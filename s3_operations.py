import boto3
import os

from src.config import config_aws

# Create an S3 client object
s3 = boto3.client('s3', aws_access_key_id=config_aws['access_key'], aws_secret_access_key=config_aws['secret_access_key'])

# Set the name of your S3 bucket and the name of the file to be uploaded
bucket_name = config_aws['bucket_name']

# Upload the file to S3
for name in ['orders_final_include.csv']:
    s3.download_file(bucket_name, f'chicks/{name}', f'data/{name}')