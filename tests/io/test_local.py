"""Test functions in owid.datautils.io.local module.

"""

import tempfile
import zipfile
from pathlib import Path

from pytest import warns, raises
from unittest.mock import patch, mock_open

from owid.datautils.io.local import decompress_file, load_json, save_json


class TestLoadJson:
    @patch("builtins.open", new_callable=mock_open, read_data='{"1": "10", "2": "20"}')
    def test_load_json_without_duplicated_keys(self, _):
        assert load_json(_) == {"1": "10", "2": "20"}

    @patch(
        "builtins.open",
        new_callable=mock_open,
        read_data='{"1": {"1_1": "1", "1_2": "2"}, "2": "20"}',
    )
    def test_load_json_without_duplicated_keys_with_more_levels(self, _):
        assert load_json(_) == {"1": {"1_1": "1", "1_2": "2"}, "2": "20"}

    @patch(
        "builtins.open",
        new_callable=mock_open,
        read_data='[{"1": {"1_1": "1", "1_2": "2"}, "2": "20"}, {"1": "10"}]',
    )
    def test_load_json_without_duplicated_keys_with_more_levels_in_a_list(self, _):
        # Here the key "1" is repeated, however, it is in a different dictionary, so it is not a duplicated key.
        assert load_json(_) == [{"1": {"1_1": "1", "1_2": "2"}, "2": "20"}, {"1": "10"}]

    @patch(
        "builtins.open",
        new_callable=mock_open,
        read_data='{"1": "10", "2": "20", "1": "100"}',
    )
    def test_load_json_with_duplicated_keys_and_no_warning(self, _):
        assert load_json(_, warn_on_duplicated_keys=False) == {"1": "100", "2": "20"}

    @patch(
        "builtins.open",
        new_callable=mock_open,
        read_data='{"1": "10", "2": "20", "1": "100"}',
    )
    def test_warn_on_load_json_with_duplicated_keys_and_warning(self, _):
        with warns(UserWarning, match="Duplicated"):
            assert load_json(_, warn_on_duplicated_keys=True) == {"1": "100", "2": "20"}

    @patch("builtins.open", new_callable=mock_open, read_data="{}")
    def test_load_empty_json(self, _):
        assert load_json(_) == {}


def test_save_json(tmpdir):
    data = {"1": "10", "2": "20"}
    save_json(data, tmpdir / "test.json")


def _create_compressed_file_with_content(file_name, containing_dir, content):
    # Create a file with some example content.
    file_inside = Path(containing_dir) / file_name
    with open(file_inside, "w") as _file_inside:
        _file_inside.write(content)
    # Compress that folder.
    with zipfile.ZipFile(file_inside.with_suffix(".zip"), "w") as zip_file:
        zip_file.write(file_inside, file_inside.name)


def _create_compressed_file_with_content_within_folder(
    file_name, containing_dir, sub_dir_name, content
):
    # Create a folder that will later be compressed.
    to_compress_dir = Path(containing_dir) / sub_dir_name
    to_compress_dir.mkdir()
    # Create a file inside that folder with some example content.
    file_inside = to_compress_dir / file_name
    with open(file_inside, "w") as _file_inside:
        _file_inside.write(content)
    # Compress that folder.
    with zipfile.ZipFile(to_compress_dir.with_suffix(".zip"), "w") as zip_file:
        zip_file.write(file_inside, file_inside.relative_to(to_compress_dir.parent))


class TestDecompressFile:
    def test_decompress_file_with_content(self, tmp_path):
        # Create a compressed file with some example content.
        example_content = "Example content."
        file_name = "example_file.txt"
        _create_compressed_file_with_content(
            file_name=file_name, containing_dir=tmp_path, content=example_content
        )
        # Decompress the original file in a new folder.
        new_dir = Path(tmp_path) / "new_dir"
        decompress_file(
            input_file=(Path(tmp_path) / file_name).with_suffix(".zip"),
            output_folder=new_dir,
        )
        # Check that, inside the new folder, we find the original (decompressed) folder and the file inside.
        recovered_file = new_dir / file_name
        assert new_dir.is_dir()
        assert recovered_file.is_file()
        # Read the file to check that its content is the expected one.
        with open(recovered_file, "r") as _recovered_file:
            assert _recovered_file.read() == example_content

    def test_decompress_file_with_content_within_folder(self, tmp_path):
        # Create a compressed file with some example content within a folder.
        example_content = "Example content."
        file_name = "example_file.txt"
        sub_dir_name = "example_dir"
        _create_compressed_file_with_content_within_folder(
            file_name=file_name,
            containing_dir=tmp_path,
            sub_dir_name=sub_dir_name,
            content=example_content,
        )
        # Decompress the original folder in a new folder.
        new_dir = Path(tmp_path) / "new_dir"
        decompress_file(
            input_file=(Path(tmp_path) / sub_dir_name).with_suffix(".zip"),
            output_folder=new_dir,
        )
        # Check that, inside the new folder, we find the original (decompressed) folder and the file inside.
        recovered_file = new_dir / sub_dir_name / file_name
        assert new_dir.is_dir()
        assert recovered_file.is_file()
        # Read the file to check that its content is the expected one.
        with open(recovered_file, "r") as _recovered_file:
            assert _recovered_file.read() == example_content

    def test_overwrite_file(self, tmp_path):
        # Create a compressed file with some example content.
        example_content = "Example content."
        file_name = "example_file.txt"
        _create_compressed_file_with_content(
            file_name=file_name, containing_dir=tmp_path, content=example_content
        )
        # Decompress the original file in a new folder.
        new_dir = Path(tmp_path) / "new_dir"
        decompress_file(
            input_file=(Path(tmp_path) / file_name).with_suffix(".zip"),
            output_folder=new_dir,
        )
        # Decompress file again and overwrite previous.
        decompress_file(
            input_file=(Path(tmp_path) / file_name).with_suffix(".zip"),
            output_folder=new_dir,
            overwrite=True,
        )
        # Check that, inside the new folder, we find the original (decompressed) folder and the file inside.
        recovered_file = new_dir / file_name
        assert new_dir.is_dir()
        assert recovered_file.is_file()
        # Read the file to check that its content is the expected one.
        with open(recovered_file, "r") as _recovered_file:
            assert _recovered_file.read() == example_content

    def test_raise_error_if_file_exists(self, tmp_path):
        # Create a compressed file with some example content.
        example_content = "Example content."
        file_name = "example_file.txt"
        _create_compressed_file_with_content(
            file_name=file_name, containing_dir=tmp_path, content=example_content
        )
        # Decompress the original file in a new folder.
        new_dir = Path(tmp_path) / "new_dir"
        decompress_file(
            input_file=(Path(tmp_path) / file_name).with_suffix(".zip"),
            output_folder=new_dir,
        )
        # Try to decompress file again, which should fail because file exists (and overwrite is by default False).
        with raises(FileExistsError):
            decompress_file(
                input_file=(Path(tmp_path) / file_name).with_suffix(".zip"),
                output_folder=new_dir,
            )
