"""S3-backed implementation of the filesystem Unit of Work.

Provides S3FileSystemUnitOfWork: an adapter that maps the Unit of Work API to
Amazon S3 (or S3-compatible services). Supports text upload, deletion, fetch,
move, upload, and listing of objects under an optional bucket prefix.

Operations are performed against a configured S3 bucket and prefix. Logging
helps capture exceptions and aid debugging.
"""

import io
import logging
import os
from urllib.parse import urlparse

import boto3

from ._base import AbstractFileSystemUnitOfWork

logger = logging.getLogger(__name__)


class S3FileSystemUnitOfWork(AbstractFileSystemUnitOfWork):
    """S3 adapter implementing the filesystem Unit of Work API.

    Maps Unit of Work methods to S3 operations, enabling text/object uploads,
    deletions, downloads, listing objects under a prefix, renames/moves, and
    changing the configured prefix or bucket.

    Attributes:
        s3_client (boto3.client): Boto3 client used to call S3 APIs.
        _bucket (str): Target S3 bucket name.
        _route (str): Prefix used to scope keys within the bucket.

    Most methods return booleans and log exceptions for troubleshooting.
    """

    def __init__(
        self,
        route: str = "",
        aws_endpoint_url: str | None = None,
        aws_region_name: str | None = None,
        bucket: str | None = None,
    ) -> None:
        """Create the S3 storage adapter and configure client and route.

        Builds a boto3 S3 client using optional custom endpoint and region, and
        resolves the bucket and prefix from the provided parameters. The
        resolved prefix is passed to the parent initializer.

        Args:
            route (str): Key prefix used within the bucket. For backward
                compatibility this can be a full S3 URI (e.g. "s3://bucket/prefix")
                or a legacy "bucket/prefix" string.
            aws_endpoint_url (str | None): Optional custom S3 endpoint (useful
                for MinIO/LocalStack). If None, the default AWS endpoint is used.
            aws_region_name (str | None): Optional AWS region name; lets boto3
                auto-detect when not provided.
            bucket (str | None): Explicit bucket name. If set, `route` is the
                prefix inside that bucket.

        """
        logger.debug("S3: Using AWS S3")
        bucket_name, route_prefix = self._resolve_bucket_and_route(bucket=bucket, route=route)
        self.s3_client = boto3.client("s3", endpoint_url=aws_endpoint_url, region_name=aws_region_name)
        self._bucket = bucket_name
        super().__init__(route=route_prefix)

    @staticmethod
    def _normalize_prefix(prefix: str | None) -> str:
        """Clean up an S3 prefix by removing surrounding slashes.

        Returns an empty string when prefix is None.
        """
        if prefix is None:
            return ""
        return prefix.strip("/")

    @classmethod
    def _resolve_bucket_and_route(cls, bucket: str | None, route: str) -> tuple[str, str]:
        """Determine the bucket name and normalized prefix from inputs.

        Accepts either an explicit bucket parameter, an S3 URI (s3://bucket/prefix),
        or a legacy "bucket/prefix" string and returns a (bucket, prefix) pair.
        """
        if route.startswith("s3://"):
            parsed = urlparse(route)
            bucket_name = bucket or parsed.netloc
            route_prefix = parsed.path.lstrip("/")
        elif bucket:
            bucket_name = bucket
            route_prefix = route
        else:
            if route.startswith("/"):
                msg = "S3 bucket is required when route is not an S3 URI."
                raise ValueError(msg)
            bucket_name, _, route_prefix = route.strip("/").partition("/")

        bucket_name = bucket_name.strip("/") if bucket_name else ""
        if not bucket_name:
            msg = "S3 bucket is required for filesystem operations."
            raise ValueError(msg)
        return bucket_name, cls._normalize_prefix(route_prefix)

    @staticmethod
    def _join_key(*parts: str | None) -> str:
        """Concatenate S3 key parts, ensuring single '/' separators.

        Skips empty parts and trims extra slashes to produce a clean key.
        """
        return "/".join(part.strip("/") for part in parts if part and part.strip("/"))

    def _object_key(self, key: str | None) -> str:
        """Create a fully-scoped S3 object key using the configured prefix.

        Combines the configured base prefix with an optional object key.
        """
        return self._join_key(self._route, key)

    def _folder_prefix(self, prefix: str | None) -> str:
        """Produce a folder-style prefix (ending with '/') under the route.

        Ensures the prefix ends with a slash so it can be used for listing objects
        under that folder.
        """
        folder_prefix = self._object_key(prefix)
        if folder_prefix and not folder_prefix.endswith("/"):
            return f"{folder_prefix}/"
        return folder_prefix

    def create_text_file(self, text: str, file: str, encoding: str = "utf-8") -> bool:
        """Upload text as an S3 object.

        Args:
            text (str): Text to upload.
            file (str): Object key (name) inside the bucket.
            encoding (str): Text encoding (default: 'utf-8').

        Returns:
            bool: True on successful upload, False otherwise.
        """
        # Encode text to bytes
        file_content = io.BytesIO(text.encode(encoding))
        # Upload the file
        key = self._object_key(file)
        try:
            self.s3_client.upload_fileobj(file_content, self._bucket, key)
        except Exception as e:
            logger.exception(f"Create text file '{file}' failed with an exception {e}.")
            return False
        return True

    def delete_file(self, file: str) -> bool:
        """Remove an object from the S3 bucket.

        Args:
            file (str): Object key to delete.

        Returns:
            bool: True if deletion succeeded, False otherwise.
        """
        key = self._object_key(file)
        try:
            self.s3_client.delete_object(Bucket=self._bucket, Key=key)
        except Exception as e:
            logger.exception(f"Delete file '{file}' failed with an exception {e}.")
            return False
        return True

    def get_file(self, file: str) -> bytes:
        """Download an object's bytes from S3.

        Args:
            file (str): Object key to retrieve.

        Returns:
            bytes: The object's content.

        Raises:
            Exception: Propagates exceptions when the key is missing or an error occurs.
        """
        key = self._object_key(file)
        try:
            response = self.s3_client.get_object(Bucket=self._bucket, Key=key)
            file_content = response["Body"].read()
            return file_content
        except Exception as e:
            logger.exception(
                f"Exception '{e}' getting object {key} from bucket {self._bucket}."
                f" Make sure they exist and "
                f"your bucket is in the same region as this function."
            )
            raise

    def list_folder(self, prefix: str) -> list:
        """List objects directly under a given prefix (non-recursive).

        Args:
            prefix (str): Folder-like prefix (e.g. 'myfolder/').

        Returns:
            list: Keys (relative to the folder) of up to 1000 objects found.
        """
        objects = []
        folder_prefix = self._folder_prefix(prefix)
        try:
            response = self.s3_client.list_objects_v2(Bucket=self._bucket, Prefix=folder_prefix)
            if "Contents" in response:
                objects = [
                    content["Key"][len(folder_prefix) :].lstrip("/")
                    for content in response.get("Contents", [])
                    if content["Key"].startswith(folder_prefix)
                ]
            return objects
        except Exception as e:
            logger.exception(
                f"Exception {e} listing objects in bucket {self._bucket}. "
                f"Make sure it exists and your bucket "
                f"is in the same region as this function."
            )
            raise

    def move_file(self, old_file: str, new_file: str, new_route: str | None = None) -> bool:
        """Copy an object to a new key (and optionally bucket), then delete the old one.

        Args:
            old_file (str): Source object key.
            new_file (str): Destination object key.
            new_route (str | None): Optional target bucket name. If None,
                the current bucket is used.

        Returns:
            bool: True when the move succeeds, False otherwise.
        """
        old_key = self._object_key(old_file)
        new_key = self._object_key(new_file)
        try:
            if new_route is None:
                new_route = self._bucket
            self.s3_client.copy_object(
                Bucket=new_route,
                CopySource={"Bucket": self._bucket, "Key": old_key},
                Key=new_key,
            )
            self.s3_client.delete_object(Bucket=self._bucket, Key=old_key)
        except Exception as e:
            logger.exception(f"Move file '{old_file}' to '{new_file}' failed with an exception {e}.")
            return False
        return True

    def move_route(self, route: str) -> str:
        """Switch the configured bucket and/or prefix.

        Args:
            route (str): New S3 route; may be an S3 URI or a bucket/prefix string.

        Returns:
            str: The route that was set.
        """
        bucket = None if route.startswith("s3://") else self._bucket
        bucket_name, route_prefix = self._resolve_bucket_and_route(bucket=bucket, route=route)
        self._bucket = bucket_name
        self._route = route_prefix
        return route

    def upload_file(self, file_route: str, name: str | None = None) -> bool:
        """Upload a local file to the configured S3 bucket.

        Args:
            file_route (str): Path to the local file to upload.
            name (str | None): Desired object key in S3. Defaults to the local
                file's basename when not provided.

        Returns:
            bool: True when upload completes successfully, False otherwise.
        """
        # If S3 object_name was not specified, use file_name
        if name is None:
            name = os.path.basename(file_route)
        # Upload the file
        key = self._object_key(name)
        try:
            self.s3_client.upload_file(file_route, self._bucket, key)
        except Exception as e:
            logger.exception(f"Upload file '{file_route}' failed with an exception {e}.")
            return False
        return True
