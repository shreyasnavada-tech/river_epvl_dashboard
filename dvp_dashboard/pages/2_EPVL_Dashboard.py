import sys
from pathlib import Path

import pandas as pd
import streamlit as st

# Resolve path imports
root_dir = Path(__file__).absolute().parent.parent.parent
sys.path.append(str(root_dir))
sys.path.append(str(Path(__file__).absolute().parent.parent))

from Home import init_google_sheets

st.set_page_config(page_title="EPVL Dashboard", page_icon="📈")

ELEC_REL_SHEET = "Mech DVP_ReliabilityVersion"


class dvp_dashboard:
    def __init__(self, tab_name):
        self.elec_rel = init_google_sheets(ELEC_REL_SHEET, tab_name)

    def uploaded_file(self):
        uploaded_file = st.file_uploader("Please upload the Zoho exported Sheet !!")
        if uploaded_file is not None:
            try:
                # 1. Read the Excel file into a Pandas DataFrame
                df = pd.read_excel(uploaded_file)
                st.success("File uploaded successfully!")
                st.markdown("### 📋 ZOHO Task details")
                st.dataframe(df)

                # Normalize column names by trimming spaces
                df.columns = df.columns.str.strip()

                # Clean rows with missing or empty Task List Names
                if "Task List Name" in df.columns:
                    df = df.dropna(subset=["Task List Name"])
                    df = df[df["Task List Name"].astype(str).str.strip() != ""]
                else:
                    st.error(
                        "Error: 'Task List Name' column not found in the uploaded file."
                    )
                    st.dataframe(df)
                    return

                # Normalize Custom Status
                status_col = (
                    "Custom Status"
                    if "Custom Status" in df.columns
                    else ("Status" if "Status" in df.columns else None)
                )
                if status_col:
                    df["Custom Status"] = df[status_col].astype(str).str.strip()
                else:
                    st.warning(
                        "'Custom Status' column not found. Creating placeholder."
                    )
                    df["Custom Status"] = "Open"

                # Task List Name ---
                st.markdown("### 📋 Individual Component wise Task status")
                total_tasks = (
                    df.groupby("Task List Name").size().reset_index(name="Total Tasks")
                )

                status_pivot = df.pivot_table(
                    index="Task List Name",
                    columns="Custom Status",
                    values="Task Name",
                    aggfunc="count",
                    fill_value=0,
                ).reset_index()

                summary_df = total_tasks.merge(
                    status_pivot, on="Task List Name", how="left"
                )
                st.dataframe(summary_df, width="stretch", hide_index=True)

                # --- 3. Tasks Overview Table ---
                st.markdown("### 📋 Tasks Owners")
                cols_to_show = ["Task List Name", "Task Name"]
                if "Owner" in df.columns:
                    cols_to_show.append("Owner")
                if "Custom Status" in df.columns:
                    cols_to_show.append("Custom Status")

                overview_df = df[cols_to_show].copy()
                if "Custom Status" in overview_df.columns:
                    overview_df.rename(
                        columns={"Custom Status": "Status"}, inplace=True
                    )

                # Order columns to: Task List Name, Task Name, Status, Owner
                columns_order = [
                    col
                    for col in ["Task List Name", "Task Name", "Status", "Owner"]
                    if col in overview_df.columns
                ]
                overview_df = overview_df[columns_order]

                st.dataframe(overview_df, width="stretch", hide_index=True)

            except Exception as e:
                st.error(f"Error reading file: {e}")


if __name__ == "__main__":
    st.header("EPVL Dashboard", width="stretch", divider="red", text_alignment="center")
    rel_dash = dvp_dashboard("RX02-Summary")
    rel_dash.uploaded_file()
