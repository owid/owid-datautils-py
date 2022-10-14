"""Library decorators."""


import functools
from owid.datautils.web import download_file_from_url
import tempfile
from typing import Callable, Any, Optional


def enable_url_download(path_arg_name: Optional[str] = None) -> Callable[[Any], Any]:
    """Enable downloading of files from URLs."""

    def _enable_url_download(func: Callable[[Any], Any]) -> Callable[[Any], Any]:
        @functools.wraps(func)
        def wrapper_download(*args: Any, **kwargs: Any) -> Any:
            # Get path to file
            _used_args = False
            if args:
                args = list(args)  # type: ignore
                path = args[0]
                _used_args = True
            else:
                path = kwargs.get(path_arg_name)  # type: ignore
                if path is None:
                    raise ValueError(
                        f"Filename was not found in args or kwargs ({path_arg_name}!"
                    )
            # Check if download is needed and download
            if (str(path).startswith("http://")) or (
                str(path).startswith("https://")
            ):  # Download from URL and run function
                with tempfile.NamedTemporaryFile() as temp_file:
                    download_file_from_url(
                        str(path), temp_file.name
                    )  # TODO: Add custom args here
                    # Modify args/kwargs
                    if _used_args:
                        args[0] = temp_file.name  # type: ignore
                    else:
                        kwargs[path_arg_name] = temp_file.name  # type: ignore
                    # Call function
                    return func(*args, **kwargs)  # type: ignore
            else:  # Run function on local file
                return func(*args, **kwargs)  # type: ignore

        return wrapper_download

    return _enable_url_download
