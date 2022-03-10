# type: ignore
"""Most logic from:
https://github.com/owid/walden/blob/master/owid/walden/owid_cache.py
"""

import os
import json
import tempfile
from os import path
from typing import Optional, Union, Tuple, Any
from mypy_boto3_s3 import S3Client

import pandas as pd
import boto3
from urllib.parse import urlparse
from botocore.exceptions import ClientError
import structlog

logger = structlog.get_logger()


class S3:
    spaces_endpoint = "https://nyc3.digitaloceanspaces.com"

    def __init__(self, profile_name: str = "default") -> None:
        self.client = self.connect(profile_name)

    def connect(self, profile_name: str = "default") -> S3Client:
        "Return a connection to Walden's DigitalOcean space."
        self.check_for_default_profile(profile_name)

        session = boto3.Session(profile_name=profile_name)
        client = session.client(
            service_name="s3",
            endpoint_url=self.spaces_endpoint,
        )
        return client

    def check_for_default_profile(self, profile_name: str) -> None:
        filename = path.expanduser("~/.aws/config")
        if (
            not path.exists(filename)
            or f"[{profile_name}]" not in open(filename).read()
        ):
            raise FileExistsError(
                f"""you must set up a config file at ~/.aws/config
it should look like:

[{profile_name}]
aws_access_key_id = ...
aws_secret_access_key = ...
                """
            )

    def upload_to_s3(
        self,
        local_path: Union[str, list[str]],
        s3_path: Union[str, list[str]],
        public: bool = False,
    ) -> Optional[str]:
        """
        Upload file to Walden.
        Args:
            local_path (Union[str, list]): Local path to file. It can be a list of paths, should match `s3_file`'s
                                            length.
            s3_path (Union[str, list]): File location to load object from. It can be a list of paths, should match
                                        `local_path`'s length.
            public (bool): Set to True to expose the file to the public (read only). Defaults to False.
        """
        print("Uploading to S3…")
        # Checks
        _check_s3_local_files(local_path, s3_path)
        # Obtain bucket & file
        bucket_name, s3_file = _url_to_path_and_bucket_mult(s3_path)
        # Upload
        extra_args = {"ACL": "public-read"} if public else {}
        try:
            self.client.upload_file(
                local_path, bucket_name, s3_file, ExtraArgs=extra_args
            )
        except ClientError as e:
            logger.error(e)
            raise UploadError(e)

        return None

    def download_from_s3(
        self,
        s3_path: Union[str, list],
        local_path: Union[str, list],
        quiet: bool = False,
    ) -> Optional[str]:
        """Download file from S3.

        Args:
            s3_path (Union[str, list]): File location to load object from.
            local_path (Union[str, list]): Path where to save file locally.
        """
        print("Downloading from S3…")
        # Checks
        _check_s3_local_files(local_path, s3_path)
        # Obtain bucket & file
        bucket_name, s3_file = _url_to_path_and_bucket_mult(s3_path)
        # Download
        try:
            self.client.download_file(bucket_name, s3_file, local_path)
        except ClientError as e:
            logger.error(e)
            raise UploadError(e)

        if not quiet:
            logger.info("DOWNLOADED", s3_path=s3_path, local_path=local_path)

    def obj_to_s3(self, obj, s3_path, public=False, **kwargs):
        """Upload an object to S3, as a file.

        Args:
            obj (object): Object to upload to S3. Currently:
                            - dict -> JSON
                            - str -> text
                            - DataFrame -> CSV/XLSX/XLS/ZIP depending on `s3_path` value.
            s3_path (srt): Object S3 file destination.
            public (bool, optional): Set to True if file is to be publicly accessed. Defaults to False.

        Raises:
            ValueError: If file format is not supported.
        """
        with tempfile.TemporaryDirectory() as f:
            output_path = os.path.join(f, "file")
            if isinstance(obj, dict):
                with open(output_path, "w") as f:
                    json.dump(obj, f)
            elif isinstance(obj, str):
                with open(output_path, "w") as file:
                    file.write(obj)
            elif isinstance(obj, pd.DataFrame):
                if s3_path.endswith(".csv") or s3_path.endswith(".zip"):
                    obj.to_csv(output_path, index=False, **kwargs)
                elif s3_path.endswith(".xls") or s3_path.endswith(".xlsx"):
                    obj.to_excel(
                        output_path, index=False, engine="xlsxwriter", **kwargs
                    )
                else:
                    raise ValueError(
                        "pd.DataFrame must be exported to either CSV or XLS/XLSX!"
                    )
            else:
                raise ValueError(
                    f"Type of `obj` is not supported ({type(obj).__name__}). Supported are json, str and pd.DataFrame"
                )
            self.upload_to_s3(local_path=output_path, s3_path=s3_path, public=public)

    def obj_from_s3(self, s3_path: str, **kwargs) -> Union[dict, str, pd.DataFrame]:
        """Load object from s3 location.

        Args:
            s3_path (str): File location to load object from.

        Returns:
            object: File loaded as object. Currently JSON -> dict, CSV/XLS/XLSV -> pd.DataFrame, general -> str
        """
        with tempfile.TemporaryDirectory() as f:
            output_path = os.path.join(f, "file")
            self.download_from_s3(s3_path=s3_path, local_path=output_path)
            if s3_path.endswith(".json"):
                with open(output_path, "r") as f:
                    return json.load(f)
            elif s3_path.endswith(".csv"):
                return pd.read_csv(output_path, **kwargs)
            elif s3_path.endswith(".xls") or s3_path.endswith(".xlsx"):
                return pd.read_excel(output_path, **kwargs)
            else:
                with open(output_path, "r") as f:
                    return f.read()

    def get_metadata(self, s3_path: str) -> Any:
        """Get metadata from file `s3_path`

        Args:
            s3_path (str): Path to S3 file.

        Returns:
            dict: Metadata
        """
        bucket_name, s3_file = s3_path_to_bucket_key(s3_path)
        response = self.client.head_object(Bucket=bucket_name, Key=s3_file)
        return response


def s3_path_to_bucket_key(url: str) -> Tuple[str, str]:
    """Get bucket and key from either s3:// URL or https:// URL."""
    parsed = urlparse(url)
    bucket = parsed.netloc
    key = parsed.path.lstrip("/")

    # strip region from bucket name in https scheme
    if parsed.scheme == "https":
        bucket = bucket.split(".")[0]

    return bucket, key


def _url_to_path_and_bucket_mult(s3_path):
    # Obtain bucket & file
    if isinstance(s3_path, list):
        bucket_name = []
        s3_file = []
        for s in s3_path:
            b, f = s3_path_to_bucket_key(s)
            bucket_name.append(b)
            s3_file.append(f)
    else:
        bucket_name, s3_file = s3_path_to_bucket_key(s3_path)
    return bucket_name, s3_file


def _check_s3_local_files(local_file, s3_path):
    if type(local_file) is not type(s3_path):
        raise TypeError("`local_file` and `s3_path` should be of the same type")
    if isinstance(local_file, list):
        if len(local_file) == len(s3_path):
            raise TypeError("`local_file` and `s3_path` should be of same length")
    elif not isinstance(local_file, str):
        raise TypeError("`local_file` and `s3_path` should be of type str or list")


def obj_to_s3(
    data: dict, s3_path: str = None, public: bool = False, **kwargs
) -> Optional[str]:
    s3 = S3()
    s3.obj_to_s3(data, s3_path, public, **kwargs)


def obj_from_s3(s3_path: Union[str, list], **kwargs) -> dict:
    s3 = S3()
    return s3.obj_from_s3(s3_path, **kwargs)


def dict_to_s3(
    data: dict, s3_path: str = None, public: bool = False, **kwargs
) -> Optional[str]:
    """Deprecated. Use `obj_to_s3` instead"""
    s3 = S3()
    s3.obj_to_s3(data, s3_path, public, **kwargs)


def str_to_s3(
    text: str, s3_path: str = None, public: bool = False, **kwargs
) -> Optional[str]:
    """Deprecated. Use `obj_to_s3` instead"""
    s3 = S3()
    s3.obj_to_s3(text, s3_path, public, **kwargs)


def df_to_s3(
    df: pd.DataFrame, s3_path: str = None, public: bool = False, **kwargs
) -> Optional[str]:
    """Deprecated. Use `obj_to_s3` instead"""
    s3 = S3()
    s3.obj_to_s3(df, s3_path, public, **kwargs)


def dict_from_s3(s3_path: Union[str, list], **kwargs) -> dict:
    """Deprecated. Use `obj_from_s3` instead"""
    s3 = S3()
    return s3.obj_from_s3(s3_path, **kwargs)


def df_from_s3(s3_path: Union[str, list], **kwargs) -> Optional[str]:
    """Deprecated. Use `obj_from_s3` instead"""
    s3 = S3()
    return s3.obj_from_s3(s3_path, **kwargs)


class UploadError(Exception):
    pass
