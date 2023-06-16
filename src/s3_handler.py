import boto3


class S3Handler:
    def __init__(self, aws_access_key, aws_secret_access_key):
        self.s3 = boto3.client(
            "s3",
            aws_access_key_id=aws_access_key,
            aws_secret_access_key=aws_secret_access_key,
        )

    def download_files(self, bucket_name, folder_name, local_path, file_names):
        for name in file_names:
            self.s3.download_file(
                bucket_name, f"{folder_name}/{name}", f"{local_path}/{name}"
            )

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
