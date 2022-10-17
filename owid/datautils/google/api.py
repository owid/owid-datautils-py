"""Google API class."""
from owid.datautils.google.sheets import GSheetApi
from owid.datautils.google.config import (
    CLIENT_SECRETS_PATH,
    CREDENTIALS_PATH,
    SETTINGS_PATH,
    google_init,
    is_google_init,
)
import gdown
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive


class GoogleApi:
    def __init__(
        self,
        clients_secrets: str = CLIENT_SECRETS_PATH,
    ) -> None:
        if clients_secrets != CLIENT_SECRETS_PATH or not is_google_init():
            google_init(clients_secrets)
        self.sheets = GSheetApi(clients_secrets, CREDENTIALS_PATH)

    @property
    def drive(self):
        gauth = GoogleAuth(settings_file=SETTINGS_PATH)
        # gauth.LocalWebserverAuth()
        drive = GoogleDrive(gauth)
        return drive

    def download_folder(self, url, output, **kwargs):
        gdown.download_folder(
            url, output=output, quiet=True, use_cookies=False, **kwargs
        )

    def download_file(self, url, output, **kwargs):
        gdown.download(url, output=output, **kwargs)

    def list_files(self, parent_id):
        drive = self.drive
        request = f"'{parent_id}' in parents and trashed=false"
        # Get list of files
        files = drive.ListFile({"q": request}).GetList()
        return files
