import boto3
from botocore.exceptions import ClientError


class S3Handler:
    def __init__(self, aws_access_key, aws_secret_access_key):
        self.s3 = boto3.client(
            "s3",
            aws_access_key_id=aws_access_key,
            aws_secret_access_key=aws_secret_access_key,
        )

    def download_files(self, bucket_name, folder_name, local_path, file_names):
        for name in file_names:
            try:
                self.s3.download_file(
                    bucket_name, f"{folder_name}/{name}", f"{local_path}/{name}"
                )
            except ClientError as e:
                if e.response["Error"]["Code"] == "404":
                    print(f"File {name} does not exist in the S3 bucket.")
                else:
                    print(f"Error downloading file {name}: {e}")

    def upload_files(self, bucket_name, folder_name, local_path, file_names):
        for name in file_names:
            self.s3.upload_file(
                f"{local_path}/{name}", bucket_name, f"{folder_name}/{name}"
            )

    def delete_files(self, bucket_name, folder_name, file_names):
        for name in file_names:
            self.s3.delete_object(Bucket=bucket_name, Key=f"{folder_name}/{name}")

    def create_folder(self, bucket_name, folder_name):
        self.s3.put_object(Bucket=bucket_name, Key=(folder_name + "/"))

    def delete_folder(self, bucket_name, folder_name):
        self.s3.delete_object(Bucket=bucket_name, Key=folder_name)

    def list_files(self, bucket_name, folder_name):
        response = self.s3.list_objects_v2(Bucket=bucket_name, Prefix=folder_name)
        files = []
        if "Contents" in response:
            for obj in response["Contents"]:
                file_name = obj["Key"].split("/")[-1]
                files.append(file_name)
        return files
