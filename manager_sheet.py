import os
from pathlib import Path

import gspread
from google.oauth2.service_account import Credentials as ServiceAccountCredentials
from pandas import DataFrame


class ManagerSheet:
    def __init__(self, file_sheet_name, spreadsheet_id, credentials_file):
        self.file_sheet_name = file_sheet_name
        self.spreadsheet_id = spreadsheet_id
        self.credentials_file = credentials_file
        self.spreadsheet = self._get_spreadsheet()

    def _get_spreadsheet(self):
        # Autenticación y acceso a Google Sheets usando google-auth
        scopes = [
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive",
        ]

        # Determine credential source: explicit, env var, or default key.json
        cred_source = self.credentials_file
        if cred_source is None:
            cred_source = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")

        if cred_source is None:
            default_path = Path(__file__).resolve().parent / "key.json"
            print(default_path)
            if default_path.exists():
                cred_source = str(default_path)

        if cred_source is None:
            raise ValueError(
                "No service account credentials provided. Set `credentials_file`, "
                "export GOOGLE_APPLICATION_CREDENTIALS, or place `key.json` next to manager_sheet.py"
            )

        # Create credentials depending on the type of cred_source
        if isinstance(cred_source, dict):
            creds = ServiceAccountCredentials.from_service_account_info(
                cred_source, scopes=scopes
            )
        elif isinstance(cred_source, (str, bytes, os.PathLike)):
            print(str(cred_source))
            creds = ServiceAccountCredentials.from_service_account_file(
                str(cred_source), scopes=scopes
            )
        else:
            raise TypeError(
                f"credentials_file must be dict, str, bytes or os.PathLike, not {type(cred_source)}"
            )

        client = gspread.authorize(creds)
        return client.open(self.file_sheet_name)

    def get_data_hoja(self, sheet_name) -> DataFrame:
        # Selecciona la hoja de Google Sheets
        try:
            worksheet = self.spreadsheet.worksheet(sheet_name)
        except gspread.WorksheetNotFound:
            # Devolver dataframe vacío si la hoja no existe
            return DataFrame()
        # Obtiene todos los valores de la hoja de cálculo
        data = DataFrame(
            worksheet.get_all_values()[1:],  # ignora la primera fila de encabezados
            columns=worksheet.get_all_values()[
                0
            ],  # obtiene la primera fila como encabezados
        )
        return data
