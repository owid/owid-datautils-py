from unittest import mock
from owid.datautils.s3 import s3_path_to_bucket_key, S3


def test_s3_path_to_bucket_key():
    url = "https://walden.nyc3.digitaloceanspaces.com/a/test.csv"
    assert s3_path_to_bucket_key(url) == ("walden", "a/test.csv")

    url = "s3://walden/a/test.csv"
    assert s3_path_to_bucket_key(url) == ("walden", "a/test.csv")

    url = "https://walden.s3.us-west-2.amazonaws.com/a/test.csv"
    assert s3_path_to_bucket_key(url) == ("walden", "a/test.csv")


@mock.patch.object(S3, "connect")
def test_download(connect_mock):
    s3 = S3()
    s3.download_from_s3(
        "https://test_bucket.nyc3.digitaloceanspaces.com/test_bucket/test.csv",
        "test.csv",
    )
    assert connect_mock.return_value.download_file.call_args_list[0].args == (
        "test_bucket",
        "test_bucket/test.csv",
        "test.csv",
    )
