import sys
from pathlib import Path

import streamlit as st

# Data used - https://docs.google.com/spreadsheets/d/1UIDqoIXhfqGMQqlidXtHTDWkxF2TW1qwNMvzrRbQjsk/edit?gid=0#gid=0

root_dir = Path(__file__).absolute().parent.parent
sys.path.append(str(root_dir))
sys.path.append(str(Path(__file__).absolute().parent))

from google_api_handler.sheet_handler import datashClient, shClients, workshClient


def init_google_sheets(sheet_name: str, tab_name: str) -> datashClient:
    xl_sheet = shClients().open_sheet(sheet_name)
    sheet_class = workshClient(xl_sheet)
    dashboard_sheet = sheet_class.select_worksheet(tab_name)
    dashboard_sheet_DH = datashClient(dashboard_sheet)
    return dashboard_sheet_DH


if __name__ == "__main__":
    st.header("DVP Dashboard", text_alignment="center", width="stretch", divider="red")

    st.markdown("")

    st.set_page_config(page_title="DVP Dashboard", page_icon="Main")
