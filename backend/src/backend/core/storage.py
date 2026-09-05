import asyncio

import boto3

from src.backend.core.settings import settings


class StorageService:
    """Wraps the S3-compatible object store used for avatar and club cover uploads."""

    def __init__(self):
        self.bucket = settings.S3_BUCKET_NAME
        self.client = boto3.client(
            "s3",
            endpoint_url=settings.S3_ENDPOINT_URL,
            aws_access_key_id=settings.S3_ACCESS_KEY,
            aws_secret_access_key=settings.S3_SECRET_KEY,
            region_name=settings.S3_REGION,
        )
        # Uploads/deletes happen over the internal endpoint, but signed URLs are
        # handed to browsers/clients, so they must be signed against the
        # publicly-reachable endpoint instead.
        self.presign_client = boto3.client(
            "s3",
            endpoint_url=settings.S3_PUBLIC_ENDPOINT_URL,
            aws_access_key_id=settings.S3_ACCESS_KEY,
            aws_secret_access_key=settings.S3_SECRET_KEY,
            region_name=settings.S3_REGION,
        )

    async def upload(self, key: str, content: bytes, content_type: str) -> None:
        """Uploads an object to the bucket.

        Args:
            key: Object key to store the content under.
            content: Raw bytes of the object.
            content_type: MIME type to store on the object.
        """
        await asyncio.to_thread(
            self.client.put_object,
            Bucket=self.bucket,
            Key=key,
            Body=content,
            ContentType=content_type,
        )

    async def delete(self, key: str) -> None:
        """Deletes an object from the bucket, ignoring missing keys.

        Args:
            key: Object key to delete.
        """
        await asyncio.to_thread(
            self.client.delete_object,
            Bucket=self.bucket,
            Key=key,
        )

    def presigned_url(self, key: str | None, expires_in: int = 900) -> str | None:
        """Generates a time-limited GET URL for an object.

        Args:
            key: Object key to sign a URL for, or None.
            expires_in: URL validity in seconds.

        Returns:
            Presigned URL string, or None if key is None.
        """
        if not key:
            return None
        return self.presign_client.generate_presigned_url(
            "get_object",
            Params={"Bucket": self.bucket, "Key": key},
            ExpiresIn=expires_in,
        )
