"""Google configuration functions."""
import os
import yaml

from pydrive.auth import GoogleAuth
from shutil import copyfile


# PATHS
CONFIG_DIR = os.path.join(os.path.expanduser("~"), ".config", "owid")
CLIENT_SECRETS_PATH = os.path.join(CONFIG_DIR, "google_client_secrets.json")
SETTINGS_PATH = os.path.join(CONFIG_DIR, "google_settings.yaml")
CREDENTIALS_PATH = os.path.join(CONFIG_DIR, "google_credentials.json")


def google_init(client_secrets: str, encoding: str = "utf8"):
    """From https://github.com/lucasrodes/whatstk/blob/bcb9cf7c256df1c9e270aab810b74ab0f7329436/whatstk/utils/gdrive.py#L38"""
    # Check client_secrets
    if not os.path.isfile(client_secrets):
        raise ValueError(f"Credentials not found at {client_secrets}. Please check!")
    # Check or build config directory
    if not os.path.isdir(CONFIG_DIR):
        os.makedirs(CONFIG_DIR, exist_ok=True)

    # Copy credentials to config folder
    copyfile(client_secrets, CLIENT_SECRETS_PATH)

    # Create settings.yaml file
    dix = {
        "client_config_backend": "file",
        "client_config_file": client_secrets,
        "save_credentials": True,
        "save_credentials_backend": "file",
        "save_credentials_file": CREDENTIALS_PATH,
        "get_refresh_token": True,
        "oauth_scope": [
            "https://www.googleapis.com/auth/drive",
            "https://www.googleapis.com/auth/drive.install",
        ],
    }
    with open(SETTINGS_PATH, "w", encoding=encoding) as f:
        yaml.dump(dix, f)

    # credentials.json
    gauth = GoogleAuth(settings_file=SETTINGS_PATH)
    gauth.CommandLineAuth()
    return gauth


def get_client_secrets_path():
    # Check settings path exists
    if not os.path.isfile(SETTINGS_PATH):
        raise FileNotFoundError(
            f"Settings file not found at {SETTINGS_PATH}. Did you run `google_init`?"
        )
    # Load settings file
    with open(SETTINGS_PATH, "r") as f:
        dix = yaml.safe_load(f)
    # Check that field `client_config_file` exists in settings file
    if "client_config_file" not in dix:
        raise KeyError("client_config_file not found in settings file.")
    # Return value
    return dix["client_config_file"]


def _check_google_config():
    if not os.path.isdir(CONFIG_DIR):
        raise FileNotFoundError(
            f"{CONFIG_DIR} folder is not created. Please check you have run"
            " `google_init`!"
        )
    if not os.path.isfile(CLIENT_SECRETS_PATH):
        raise FileNotFoundError(
            f"Credentials not found at {CLIENT_SECRETS_PATH}. Please check you have run"
            " `google_init`!"
        )
    for f in [CREDENTIALS_PATH, SETTINGS_PATH]:
        if not os.path.isfile(f):
            raise FileNotFoundError(
                f"{f} file was not found. Please check you have run `google_init`!"
            )


def is_google_init():
    try:
        _check_google_config()
    except FileNotFoundError:
        return False
    return True
