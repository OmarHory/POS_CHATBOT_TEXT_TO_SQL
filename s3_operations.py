import boto3
from src.config import config_aws
import argparse
import os
from dotenv import load_dotenv

load_dotenv()

aws_access_key = os.getenv("aws_access_key")
aws_secret_access_key = os.getenv("aws_secret_access_key")
aws_bucket_name = os.getenv("aws_bucket_name")
aws_folder_name = os.getenv("aws_s3_folder")
client_id = os.getenv("client_id")


parser = argparse.ArgumentParser(description="Process method argument")

parser.add_argument(
    "method",
    choices=["download", "upload"],
    help="Specify the method: download or upload",
)

args = parser.parse_args()

method = args.method

s3 = boto3.client(
    "s3", aws_access_key_id=aws_access_key, aws_secret_access_key=aws_secret_access_key
)

if method == "download":
    print("Performing download...")

    for name in ["orders_final_include.csv"]:
        s3.download_file(aws_bucket_name, f"{aws_folder_name}/{name}", f"data/{client_id}/raw/{name}")
elif method == "upload":
    print("Performing upload...")
    for name in ["orders_final_include_updated.csv"]:
        s3.upload_file(
            f"data/{client_id}/raw/{name}",
            aws_bucket_name,
            f"{aws_folder_name}/orders_final_include.csv",
        )

else:
    raise ValueError("Invalid method specified")
