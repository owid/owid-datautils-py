"""Google Sheet utils."""
import os
from gsheets import Sheets
from gsheets.models import SpreadSheet, WorkSheet

from owid.datautils.google.config import CLIENT_SECRETS_PATH, CREDENTIALS_PATH

# CREDENTIALS_PATH


class GSheetApi:
    """Interface to interact with Google sheets."""

    def __init__(
        self,
        clients_secrets: str = CLIENT_SECRETS_PATH,
        credentials_path: str = CREDENTIALS_PATH,
    ) -> None:
        self.clients_secrets = clients_secrets
        self.credentials_path = credentials_path
        self._init_config_folder()
        self.__sheets = None

    @property
    def sheets(self) -> Sheets:
        """Access or initialize sheets attribute."""
        if self.__sheets is None:
            self.__sheets = Sheets.from_files(
                self.clients_secrets, self.credentials_path, no_webserver=True
            )
        return self.__sheets

    def _init_config_folder(self) -> None:
        credentials_folder = os.path.expanduser(os.path.dirname(self.credentials_path))
        if not os.path.isdir(credentials_folder):
            os.makedirs(credentials_folder, exist_ok=True)

    def get_sheet(self, sheet_id: str) -> SpreadSheet:
        """Get entire Google sheet.

        Parameters
        ----------
        sheet_id : str
            ID of the sheet.

        Returns
        -------
        SpreadSheet
            SpreadSheet with given `sheet_id`.
        """
        return self.sheets.get(sheet_id)

    def get_worksheet(self, sheet_id: str, worksheet_title: str) -> WorkSheet:
        """Get a worksheet from a Google sheet.

        Parameters
        ----------
        sheet_id : str
            ID of the sheet.
        worksheet_title : str
            Title of the worksheet.

        Returns
        -------
        WorkSheet
            Worksheet from sheet with id `sheet_id` and tab title `worksheet_title`.
        """
        sheet = self.sheets.get(sheet_id)
        try:
            return sheet.find(worksheet_title)
        except KeyError:
            raise KeyError(f"No worksheet with title {worksheet_title} was found.")
