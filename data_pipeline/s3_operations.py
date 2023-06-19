import os
import sys
from dotenv import load_dotenv

parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(parent_dir)

from src.s3_handler import S3Handler
from src.helpers.utils import list_csv_files_in_directory
import argparse

load_dotenv()

parser = argparse.ArgumentParser()
parser.add_argument('--client-id', type=int, required=True, help='Client ID')
parser.add_argument('--method', type=str, required=True, help='Method to run')
parser.add_argument('--local_data_folder', type=str, required=True, help='local_data_folder to do operation -> raw, processed, updates')
parser.add_argument('--aws_data_folder', type=str, required=True, help='aws_data_folder to do operation -> raw, processed, updates')
parser.add_argument('--files', nargs='+', type=str, help='Specific file names to download or delete')

args = parser.parse_args()
client_id = args.client_id
method = args.method
local_data_folder = args.local_data_folder
aws_data_folder = args.aws_data_folder
files = args.files

# Environment Variables
aws_access_key = os.getenv("aws_access_key")
aws_secret_access_key = os.getenv("aws_secret_access_key")
bucket_name = os.getenv("aws_bucket_name")
aws_folder_path = f"{client_id}/{aws_data_folder}"
local_path = f"data/{client_id}/{local_data_folder}"

if method not in ['upload', 'download', 'delete']:
    raise Exception('Invalid method')

handler = S3Handler(aws_access_key, aws_secret_access_key)

if method == 'upload':
    csv_files = list_csv_files_in_directory(f'data/{client_id}/{local_data_folder}')
    if len(csv_files) == 0:
        raise Exception('No CSV files found')
    if files is not None:
        csv_files = [os.path.basename(file) for file in files]
    handler.upload_files(bucket_name, aws_folder_path, local_path, csv_files)

elif method == 'download':
    if files is None:
        files = handler.list_files(bucket_name, aws_folder_path)

    if len(files) == 0:
        raise Exception('No files found in S3')

    handler.download_files(bucket_name, aws_folder_path, local_path, files)

elif method == 'delete':
    if files is None:
        files = handler.list_files(bucket_name, aws_folder_path)

    if len(files) == 0:
        raise Exception('No files found in S3')

    handler.delete_files(bucket_name, aws_folder_path, files)
