import boto3
import argparse
import os
from dotenv import load_dotenv

load_dotenv()

def main():
    aws_access_key = os.getenv("aws_access_key")
    aws_secret_access_key = os.getenv("aws_secret_access_key")
    aws_bucket_name = os.getenv("aws_bucket_name")
    aws_folder_name = os.getenv("aws_s3_folder")
    client_id = os.getenv("client_id")

    parser = argparse.ArgumentParser(description="Process method and file names arguments")
    parser.add_argument("method", choices=["download", "upload"], help="Specify the method: download or upload")
    parser.add_argument("file_names", nargs="+", help="Specify the CSV file names")
    args = parser.parse_args()
    method = args.method
    file_names = args.file_names

    s3 = boto3.client("s3", aws_access_key_id=aws_access_key, aws_secret_access_key=aws_secret_access_key)

    if method == "download":
        print("Performing download...")
        download_files(s3, aws_bucket_name, aws_folder_name, client_id, file_names)
    elif method == "upload":
        print("Performing upload...")
        upload_files(s3, aws_bucket_name, aws_folder_name, client_id, file_names)
    else:
        raise ValueError("Invalid method specified")

def download_files(s3, bucket_name, folder_name, client_id, file_names):
    for name in file_names:
        s3.download_file(bucket_name, f"{folder_name}/{name}", f"data/{client_id}/raw/{name}")

def upload_files(s3, bucket_name, folder_name, client_id, file_names):
    for name in file_names:
        s3.upload_file(f"data/{client_id}/raw/{name}", bucket_name, f"{folder_name}/{name}")

if __name__ == "__main__":
    main()
