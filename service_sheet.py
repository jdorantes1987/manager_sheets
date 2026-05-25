import os
from pathlib import Path

import gspread
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build


class ServiceSheet:
    def __init__(self, spreadsheet_id, file_name, credentials_file):
        self.__spreadsheet_id = spreadsheet_id
        self.__file_name = file_name
        self.__credentials_file = credentials_file
        # Validar que se haya pasado una ruta de credenciales
        if not self.__credentials_file:
            raise ValueError(
                "Credentials file path is required. Set environment variable CGIMPRENTA_CREDENTIALS or pass a valid path."
            )
        # Aceptar rutas relativas y absolutas; verificar existencia
        if not os.path.isfile(self.__credentials_file):
            raise FileNotFoundError(
                f"Credentials file not found: {self.__credentials_file}"
            )

        self.__service = self._get_service()

    def _get_service(self):
        scopes = ["https://www.googleapis.com/auth/spreadsheets"]
        creds = Credentials.from_service_account_file(
            self.__credentials_file, scopes=scopes
        )
        return build("sheets", "v4", credentials=creds)

    def get_spreadsheet(self):
        # Autenticación y acceso a Google Sheets usando google-auth
        scopes = [
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive",
        ]

        # Determine credential source: explicit, env var, or default key.json
        cred_source = self.__credentials_file
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
            creds = Credentials.from_service_account_info(cred_source, scopes=scopes)
        elif isinstance(cred_source, (str, bytes, os.PathLike)):
            print(str(cred_source))
            creds = Credentials.from_service_account_file(
                str(cred_source), scopes=scopes
            )
        else:
            raise TypeError(
                f"credentials_file must be dict, str, bytes or os.PathLike, not {type(cred_source)}"
            )

        client = gspread.authorize(creds)
        return client.open(self.__file_name)
