import sys
from pathlib import Path
from typing import Any, List, Optional

import gspread
from dateutil.parser import isoparse

path = str(
    Path(Path(Path(__file__).parent.absolute()).parent.absolute()).parent.absolute()
)
sys.path.insert(0, path)

# Documentation of gspread library - https://docs.gspread.org/en/latest/index.html, https://docs.gspread.org/en/latest/user-guide.html


class shClients:
    """
    This is the master class that handles opening and editing of a google sheet workbook. It initializes a Google spreadsheet object.
    """

    def __init__(self):
        # TODO: Credentials is a json that contains the key for google API auth. This is currently linked to nagendrar@riderriver.com account. Needs to be moved to a general account
        creds_file = "oauth_creds.json"
        
        # If running locally, the file will exist
        if Path(creds_file).exists() or Path("utility_scripts/google_api_handler/" + creds_file).exists():
            self.shClient = gspread.oauth(credentials_filename=creds_file)
        else:
            # If running on Streamlit Cloud, read from st.secrets and create a temp file
            import streamlit as st
            import json
            import tempfile
            import os
            
            # Read credentials from Streamlit secrets
            creds_dict = dict(st.secrets["google_oauth"])
            
            # Create a temporary file to store the credentials so gspread can read it
            with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".json") as f:
                json.dump(creds_dict, f)
                temp_creds_path = f.name
                
            self.shClient = gspread.oauth(credentials_filename=temp_creds_path)
            
            # Clean up the temp file after authentication
            try:
                os.remove(temp_creds_path)
            except Exception:
                pass

        self.shMan = None

    @property
    def get_current_sheet(self) -> Any:
        return self.shMan

    def open_sheet(
        self,
        name: Optional[str] = None,
        sheet_id: Optional[str] = None,
        url: Optional[str] = None,
    ) -> Any:
        """
        This method supports opening a sheet using multiple ways - https://docs.gspread.org/en/latest/user-guide.html
        Using name, sheet_id or the url of the page

        Returns: A google sheet object
        """
        if name:
            self.shMan = self.shClient.open(name)
            return self.shMan
        elif sheet_id:
            self.shMan = self.shClient.open_by_key(sheet_id)
            return self.shMan
        elif url:
            self.shMan = self.shClient.open_by_url(url)
            return self.shMan

    def create_sheet(self, sheet_name: str) -> Any:
        return self.shClient.create(sheet_name)


class workshClient:
    """This is the class that handles opening and editing of individual sheets/tabs in a given google sheet. It initializes a individual sheet object."""

    def __init__(self, sheet: Any):
        self.shMan = sheet

    def get_last_updated_timestamp(self, epoch: bool = True) -> float:
        if epoch == True:
            return isoparse(self.shMan.get_lastUpdateTime()).timestamp()
        return self.shMan.get_lastUpdateTime()

    @property
    def get_current_worksheet(self) -> Any:
        return self.WorkshMan

    def select_worksheet(self, ws_name: Optional[str] = None) -> Any:
        """This method allows user to select the worksheet based on the name"""
        if ws_name:
            self.WorkshMan = self.shMan.worksheet(ws_name)
            return self.WorkshMan
        return self.WorkshMan

    def list_all_worksheets(self) -> list:
        return self.shMan.worksheets()


class datashClient:
    """This is the class that handles opening and editing of DATA present in individual sheets/tabs"""

    def __init__(self, worksheet: Any):
        self.data = worksheet

    def update_cell_values(
        self,
        value: Any,
        cell_anot: Optional[str] = None,
        coords: Optional[tuple[int, int]] = None,
    ) -> Any:
        """
        This method supports updating cell values using multiple ways - https://docs.gspread.org/en/latest/user-guide.html
        Using Cell anot i.e A3, H2 or using coords i.e (row, col) (1, 2)

        Returns: Value
        """
        if cell_anot:
            return self.data.update_acell(cell_anot, value)
        elif coords:
            return self.data.update_cell(coords[0], coords[1], value)

    def get_cell_value(
        self, cell_anot: Optional[str] = None, coords: Optional[tuple] = None
    ) -> Any:
        """
        This method supports getting cell values using multiple ways - https://docs.gspread.org/en/latest/user-guide.html
        Using Cell anot i.e A3, H2 or using coords i.e (row, col) (1, 2)

        Returns: Value
        """
        if cell_anot:
            return self.data.acell(cell_anot).value
        elif coords:
            return self.data.cell(coords[0], coords[1]).value

    def get_all_values(self) -> List[List]:
        return self.data.get_all_values()

    def get_all_row_values(self, index: int) -> Any:
        return self.data.row_values(index)

    def get_all_coloumn_values(self, index: int) -> Any:
        return self.data.col_values(index)

    def batch_update_values(self, body):
        return self.data.batch_update(body)

    @staticmethod
    def get_a1_notation_for_chords(row: int, col: int) -> str:
        """
        Provided coordinates - (0,0), returns A1
        """
        letter = ""
        while col >= 0:
            letter = chr(65 + (col % 26)) + letter
            col = (col // 26) - 1
        return letter + str(row + 1)


if __name__ == "__main__":
    # Unit tests

    # a = shClients()
    # b = a.open_sheet(name="sample")
    # c = workshClient(b)
    # d = c.select_worksheet("IDC")
    # print(d)
    # e = datashClient(d)
    # body = [
    #     {
    #         "range": "N1",
    #         "values": [["2000"]],
    #     }
    # ]
    # e.batch_update_values(body)
    # print(e.get_a1_notation_for_chords(0, 1))
    # print(e.get_cell_value(coords=(2,2)))
    # print(e.get_all_row_values(1))
    # print(e.get_all_coloumn_values(1))
    # print(e.update_cell(value='goobe', coords=(30,5)))
    # # print(a.create_sheet('goobe'))
    # # url='https://docs.google.com/spreadsheets/d/1sRNQg9JZZYnBEYf-CsapHmH6MK1zfnRVeYhdmSxZE2w/edit?gid=0#gid=0'
    # print(latLongLib.get_location_address((12.980682, 77.714462)))
    pass
