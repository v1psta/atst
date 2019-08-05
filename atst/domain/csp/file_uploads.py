from azure.storage.common import CloudStorageAccount
from azure.storage.blob import ContainerPermissions
from datetime import datetime, timedelta
from uuid import uuid4

import boto3


def build_uploader(config):
    csp = config.get("CSP")
    if csp == "aws":
        return AwsUploader(config)
    elif csp == "azure":
        return AzureUploader(config)
    else:
        return MockUploader(config)


class Uploader:
    def generate_token(self):
        pass

    def object_name(self):
        return str(uuid4())


class MockUploader(Uploader):
    def __init__(self, config):
        self.config = config

    def get_token(self):
        return ({}, self.object_name())


class AzureUploader(Uploader):
    def __init__(self, config):
        self.config = config

    def get_token(self):
        """
        Generates an Azure SAS token for pre-authorizing a file upload.

        Returns a tuple in the following format: (token_dict, object_name), where
            - token_dict has a `token` key which contains the SAS token as a string
            - object_name is a string
        """
        account = CloudStorageAccount(
            account_name=self.config["AZURE_ACCOUNT_NAME"],
            account_key=self.config["AZURE_STORAGE_KEY"],
        )
        bbs = account.create_block_blob_service()
        object_name = self.object_name()
        sas_token = bbs.generate_container_shared_access_signature(
            self.config["AZURE_TO_BUCKET_NAME"],
            ContainerPermissions.WRITE,
            datetime.utcnow() + timedelta(minutes=15),
        )
        return ({"token": sas_token}, object_name)


class AwsUploader(Uploader):
    def __init__(self, config):
        self.config = config

    def get_token(self):
        """
        Generates an AWS presigned post for pre-authorizing a file upload.

        Returns a tuple in the following format: (token_dict, object_name), where
            - token_dict contains several fields that will be passed directly into the
              form before being sent to S3
            - object_name is a string
        """
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
