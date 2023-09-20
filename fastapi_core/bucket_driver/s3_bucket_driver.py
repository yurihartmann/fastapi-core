from tempfile import TemporaryFile

from platform_core.bucket_driver.bucket_driver_abc import BucketDriverABC


class S3BucketDriver(BucketDriverABC):

    def __init__(self, s3_client, bucket: str):
        self.s3_client = s3_client
        self.bucket = bucket

    async def download_file(self, file_path: str, *args, **kwargs) -> TemporaryFile:
        file = TemporaryFile()
        self.s3_client.download_fileobj(
            Bucket=self.bucket,
            Key=file_path,
            Fileobj=file,
            *args,
            **kwargs
        )
        file.seek(0)
        return file

    async def upload_file(self, file: bytes, file_path: str, *args, **kwargs):
        self.s3_client.put_object(
            Body=file,
            Bucket=self.bucket,
            Key=file_path,
            *args,
            **kwargs
        )
