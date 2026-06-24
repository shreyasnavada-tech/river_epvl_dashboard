import sys
from pathlib import Path

import pandas as pd
import streamlit as st

root_dir = Path(__file__).absolute().parent.parent.parent
sys.path.append(str(root_dir))
sys.path.append(str(Path(__file__).absolute().parent.parent))
# adding this for resolving path issue

st.set_page_config(page_title="Electrical Reliability", page_icon="📈")

ELEC_REL_SHEET = "Mech DVP_ReliabilityVersion"

from Home import init_google_sheets


class dvp_dash:
    def __init__(self, tab_name):
        self.elec_rel = init_google_sheets(ELEC_REL_SHEET, tab_name)

    def fetch_horizontal_table(
        self, start_row: int, end_row: int, star_col: int, end_col: int
    ):
        _temp_list = []
        for value in range(start_row, end_row):
            _temp_list.append(self.elec_rel.get_all_row_values(value)[star_col:end_col])
        return _temp_list

    def fetch_vertical_table(self, start_col: int, end_col: int) -> list:
        _temp = []
        for val in range(start_col, end_col):
            _temp.append(self.elec_rel.get_all_coloumn_values(val))

        return _temp


if __name__ == "__main__":

    st.header(
        "Reliability Dashboard", width="stretch", divider="red", text_alignment="center"
    )
    rel_dash = dvp_dash("RX02-Summary")

    st.subheader("Stage Wise Risk Assessment")
    stage_wise_risk_assessment_df = rel_dash.fetch_horizontal_table(1, 4, 4, 9)
    risk_df = pd.DataFrame(
        {
            stage_wise_risk_assessment_df[0][0]: stage_wise_risk_assessment_df[0][1:],
            stage_wise_risk_assessment_df[1][0]: stage_wise_risk_assessment_df[1][1:],
            stage_wise_risk_assessment_df[2][0]: stage_wise_risk_assessment_df[2][1:],
        }
    )
    st.dataframe(risk_df, hide_index=True)

    st.subheader("Component Level Risk Assessment")
    component_level_risk_data = rel_dash.fetch_vertical_table(1, 4)

    comp_df = pd.DataFrame(
        {
            component_level_risk_data[0][0]: component_level_risk_data[0][1:],
            component_level_risk_data[1][0]: component_level_risk_data[1][1:]
            + ["0"]
            * (
                len(component_level_risk_data[0][1:])
                - len(component_level_risk_data[1][1:])
            ),
            component_level_risk_data[2][0]: component_level_risk_data[2][1:]
            + ["0"]
            * (
                len(component_level_risk_data[0][1:])
                - len(component_level_risk_data[1][1:])
            ),
        }
    )
    st.dataframe(comp_df.iloc[1:], hide_index=True)

    st.subheader("Vehicle RD confidence")
    vehicle_vd_confidence_data = rel_dash.fetch_vertical_table(11, 14)
    vehicle_vd_df = pd.DataFrame(
        {
            vehicle_vd_confidence_data[1][0]: vehicle_vd_confidence_data[1][1:],
            vehicle_vd_confidence_data[2][0]: vehicle_vd_confidence_data[2][1:],
        }
    )

    st.dataframe(vehicle_vd_df.iloc[1:], hide_index=True)
    st.header(
        f"Vehicle RD confidence - {vehicle_vd_confidence_data[0][1]}%", divider="red"
    )
