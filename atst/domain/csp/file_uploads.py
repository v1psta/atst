from azure.storage.common import CloudStorageAccount
from azure.storage.blob import ContainerPermissions
from datetime import datetime, timedelta
from uuid import uuid4

import boto3


def build_uploader(config):
    if config["CSP"] == "aws":
        return AwsUploader(config)
    elif config["CSP"] == "azure":
        return AzureUploader(config)


class Uploader:
    def generate_token(self):
        pass

    def object_name(self):
        return str(uuid4())


class AzureUploader(Uploader):
    def __init__(self, config):
        self.config = config

    def get_token(self):
        account = CloudStorageAccount(
            account_name="atat", account_key=self.config["AZURE_STORAGE_KEY"]
        )
        bbs = account.create_block_blob_service()
        object_name = self.object_name()
        sas_token = bbs.generate_container_shared_access_signature(
            "task-order-pdfs",
            ContainerPermissions.WRITE,
            datetime.utcnow() + timedelta(minutes=15),
        )
        return ({"token": sas_token}, object_name)


class AwsUploader(Uploader):
    def __init__(self, config):
        self.config = config

    def get_token(self):
        s3_client = boto3.client(
            "s3",
            aws_access_key_id=self.config["AWS_ACCESS_KEY_ID"],
            aws_secret_access_key=self.config["AWS_SECRET_KEY"],
            config=boto3.session.Config(
                signature_version="s3v4", region_name=self.config["AWS_REGION_NAME"]
            ),
        )
        object_name = self.object_name()
        presigned_post = s3_client.generate_presigned_post(
            self.config["AWS_BUCKET_NAME"],
            object_name,
            ExpiresIn=3600,
            Conditions=[
                ("eq", "$Content-Type", "application/pdf"),
                ("starts-with", "$x-amz-meta-filename", ""),
            ],
            Fields={"Content-Type": "application/pdf", "x-amz-meta-filename": ""},
        )
        return (presigned_post, object_name)
