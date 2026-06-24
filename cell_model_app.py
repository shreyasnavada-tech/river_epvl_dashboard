import pandas as pd
import streamlit as st
from google_api_handler.sheet_handler import datashClient, shClients, workshClient

CELL_MANUFACTURER = 0
CELL_CAPACITY = 1

# Data used - https://docs.google.com/spreadsheets/d/1Ei8G2xJfnpE3Ot8RHxXzJqDxuXJfOlULnjeoUUUXl7Q/edit?gid=986180834#gid=986180834


def init_google_sheets(sheet_name: str, tab_name: str) -> datashClient:
    xl_sheet = shClients().open_sheet(sheet_name)
    sheet_class = workshClient(xl_sheet)
    dashboard_sheet = sheet_class.select_worksheet(tab_name)
    dashboard_sheet_DH = datashClient(dashboard_sheet)
    return dashboard_sheet_DH


def rank_generator(button: str, temp: int):
    dashboard_sheet_DH = init_google_sheets("Cell Model", "Cell Data")
    all_cell_mans_orig = dashboard_sheet_DH.get_all_coloumn_values(2)
    coloumn_length = int(len(all_cell_mans_orig))
    temperature_values = [
        val for val in dashboard_sheet_DH.get_all_coloumn_values(1)[1:] if val != ""
    ]
    temp_values_len = int(len(temperature_values))

    index = temperature_values.index(str(temp))

    # If index is 0, that temp is the next set of values i.e (total_col_length/total_temp_values)*index.
    # If there are 3 temp and total_length of any other coloumn is 21: the first temp values start from 0 to 7 excluding heading row.
    # Second starts from 8 till 14 and third from 15 to 21
    factor = (int((coloumn_length - 1) / temp_values_len)) * index

    slice_upper_limit = int(factor + (coloumn_length - 1) / temp_values_len)

    # Slicing data from 1 to 7 instead of 0 to 6 to avoid the heading row
    rated_capacity_list = dashboard_sheet_DH.get_all_coloumn_values(3)[
        factor + 1 : slice_upper_limit + 1
    ]
    measured_capacity_list = dashboard_sheet_DH.get_all_coloumn_values(4)[
        factor + 1 : slice_upper_limit + 1
    ]
    avg_temp_list = dashboard_sheet_DH.get_all_coloumn_values(11)[
        factor + 1 : slice_upper_limit + 1
    ]
    soh_list = dashboard_sheet_DH.get_all_coloumn_values(9)[
        factor + 1 : slice_upper_limit + 1
    ]
    dcir_list = dashboard_sheet_DH.get_all_coloumn_values(8)[
        factor + 1 : slice_upper_limit + 1
    ]

    data_list = pd.DataFrame(
        {
            "Cell Manufacturer": all_cell_mans_orig[factor + 1 : slice_upper_limit + 1],
            "Rated Capacity": rated_capacity_list,
            "Measured Capacity": measured_capacity_list,
            "Average Temperature": avg_temp_list,
            "SOH": soh_list,
            "DCIR": dcir_list,
            "Score": [0] * len(rated_capacity_list),
        }
    )

    if button == "5Ah":
        data_list = data_list[data_list["Rated Capacity"] == "5.00"]

    else:
        data_list = data_list[data_list["Rated Capacity"] != "5.00"]

    for param in data_list.columns.to_list()[2:-1]:
        if param in ("DCIR", "Average Temperature"):
            eq_value = data_list[param].idxmin()
        else:
            eq_value = data_list[param].idxmax()
        rank = 2
        if param in ("SOH", "DCIR"):
            rank = 3
        data_list["Score"][eq_value] += rank

    # Dropping index
    data_list.set_index("Cell Manufacturer", inplace=True)

    # Sorting by Score and then by the highest SOH if scores are equal
    st.write(data_list.sort_values(by=["Score", "SOH"], ascending=False))


st.title("Cell Model - Rank Generator")
dashboard_sheet_DH = init_google_sheets("Cell Model", "Cell Data")
temperature_values = [
    val for val in dashboard_sheet_DH.get_all_coloumn_values(1)[1:] if val != ""
]
cell_select = st.selectbox("Select Cell Ah", options=["5Ah", "Above 5Ah"], index=None)
temp_select = st.selectbox("Select Temperature", options=temperature_values, index=None)

st.text("""
    How is the Score computed ?
        Score is sum of the weights assigned to each parameter. Listed below are the weights of the paramaters:
    """)

description_df = pd.DataFrame(
    {
        "Parameter": ["Measured Capacity", "SOH", "Average Temperature", "DCIR"],
        "Weight": [
            "2 for the Highest value",
            "3 for the Highest value",
            "2 for the Lowest value",
            "3 for the Lowest value",
        ],
    }
)

# Dropping index
description_df.set_index("Parameter", inplace=True)
st.table(description_df)

st.subheader("Computed Score")
if cell_select and temp_select:
    rank_generator(cell_select, temp_select)
