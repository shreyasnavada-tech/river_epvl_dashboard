import pandas as pd
import streamlit as st
from google_api_handler.sheet_handler import datashClient, shClients, workshClient

# Data used - https://docs.google.com/spreadsheets/d/14W36vrqgBftburHzI0H0qa9lTEkHMmt7JYnUb1C6Tfw/edit?gid=0#gid=0


def init_google_sheets(sheet_name: str, tab_name: str) -> datashClient:
    xl_sheet = shClients().open_sheet(sheet_name)
    sheet_class = workshClient(xl_sheet)
    dashboard_sheet = sheet_class.select_worksheet(tab_name)
    dashboard_sheet_DH = datashClient(dashboard_sheet)
    return dashboard_sheet_DH


st.set_page_config(layout="wide")

st.title("Material Change vs Tests Map", text_alignment="center")


# Init google sheets
dashboard_sheet_DH = init_google_sheets(
    "Validation Requirements for Product Changes", "Sheet1"
)

# Get material changes coloumn values
all_mat_changes_values = dashboard_sheet_DH.get_all_coloumn_values(2)[2:]
material_changes_list = [val for val in all_mat_changes_values if val != ""]

# Get tests list coloumn values
test_changes_values = dashboard_sheet_DH.get_all_coloumn_values(4)[2:]
test_changes_list = [val for val in test_changes_values if val != ""]

# Get test length coloumn values
all_test_len_values = dashboard_sheet_DH.get_all_coloumn_values(6)[2:]
len_tests = [val for val in all_test_len_values if val != ""]

# Standards
standard_values = dashboard_sheet_DH.get_all_coloumn_values(5)[2:]
standards_list = [val for val in standard_values if val != ""]

# Type of test
test_types = dashboard_sheet_DH.get_all_coloumn_values(7)[2:]
test_types_list = [val for val in test_types if val != ""]

# Duration
duration_values = dashboard_sheet_DH.get_all_coloumn_values(8)[2:]
duration_values_list = [val for val in duration_values if val != ""]

# Priority of tests
priority_values = dashboard_sheet_DH.get_all_coloumn_values(9)[2:]
priority_values_list = [val for val in priority_values if val != ""]

# Failure Mode
failure_modes = dashboard_sheet_DH.get_all_coloumn_values(10)[2:]
failure_modes_list = [val for val in failure_modes if val != ""]

# Compute the end value of a test by adding the starting value and len of tests from len_tests var
end_index_compute = []
temp = 0
for val in len_tests:
    val = int(temp) + int(val)
    temp = val
    end_index_compute.append(int(val))

dropdown_material = st.selectbox(
    "Select Material Change", options=material_changes_list, index=None
)

# Create a tuple with start and end index
test_length_tuple = []
for st_index, end_index in zip(len_tests, end_index_compute):
    test_length_tuple.append((int(st_index), end_index))
tests_vs_len_map = dict(zip(material_changes_list, test_length_tuple))

if dropdown_material is not None:
    total_length = tests_vs_len_map[dropdown_material]
    last_val = total_length[1]
    first_val = total_length[1] - total_length[0]
    df = pd.DataFrame(
        {
            "Tests": test_changes_list[first_val:last_val],
            "Standard": standards_list[first_val:last_val],
            "Test Type": test_types_list[first_val:last_val],
            "Duration in hours": duration_values_list[first_val:last_val],
            "Priority": priority_values_list[first_val:last_val],
            "Failure Modes": failure_modes_list[first_val:last_val],
        }
    )

    st.dataframe(df, hide_index=True)
    duration_df = pd.DataFrame(
        [
            {
                "Max Report Duration in Hours": max(
                    duration_values_list[first_val:last_val], key=int
                )
            }
        ]
    )
    st.dataframe(duration_df, hide_index=True)
