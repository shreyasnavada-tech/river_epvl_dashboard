import sys
from pathlib import Path

import altair as alt
import pandas as pd
import streamlit as st

root_dir = Path(__file__).absolute().parent.parent.parent
sys.path.append(str(root_dir))
sys.path.append(str(Path(__file__).absolute().parent.parent))
# adding this for resolving path issue

st.set_page_config(page_title="RX02 Dashboard", page_icon="📈")

SHEET = "RX02_Dashboard"

from Home import init_google_sheets


class RX02_Dash:
    def __init__(self, sheet_name: str, tab_name: str):
        self.rx02_dash = init_google_sheets(sheet_name, tab_name)

    def fetch_horizontal_table(
        self, start_row: int, end_row: int, star_col: int, end_col: int
    ):
        _temp_list = []
        for value in range(start_row, end_row):
            _temp_list.append(
                self.rx02_dash.get_all_row_values(value)[star_col:end_col]
            )
        return _temp_list

    def fetch_vertical_table(self, start_col: int, end_col: int) -> list:
        _temp = []
        for val in range(start_col, end_col):
            _temp.append(self.rx02_dash.get_all_coloumn_values(val))

        return _temp


if __name__ == "__main__":
    st.header("RX02 Dashboard", width="stretch", divider="red", text_alignment="center")

    dashb = RX02_Dash(SHEET, "Sheet1")
    # A. Scope and Stage component
    st.subheader("Scope and Stage of Component")
    scope_stage_component = dashb.fetch_horizontal_table(4, 18, 25, 30)
    column_scope = ["Components/Phase", "Alpha P1", "Alpha P2", "Beta", "T0"]
    df1 = pd.DataFrame(scope_stage_component, columns=column_scope)
    styled_df = df1.style.apply(
        lambda _: [
            "background-color: yellow" if col == "Alpha P2" else ""
            for col in df1.columns
        ],
        axis=1,
    )
    df1 = df1.set_index("Components/Phase")
    st.dataframe(df1)

    st.subheader(f"Component Testing Phase Data")

    # Fetch data
    scope_sample_requested = dashb.fetch_horizontal_table(25, 31, 1, 12)
    scope_validation_confidence = dashb.fetch_horizontal_table(25, 31, 15, 26)

    # --- 1. DYNAMICALLY PARSE ROWS & FORWARD-FILL (DATASET 1) ---
    raw_timeline_row = scope_sample_requested[0][1:]
    raw_phase_row = scope_sample_requested[1][1:]
    data_rows = scope_sample_requested[2:]

    filled_phases = []
    current_phase = ""
    for phase in raw_phase_row:
        if phase and str(phase).strip() not in ["", "-", "?"]:
            current_phase = str(phase).strip()
        filled_phases.append(current_phase)

    phase_spans = []
    if filled_phases:
        current_p = filled_phases[0]
        count = 1
        for p in filled_phases[1:]:
            if p == current_p:
                count += 1
            else:
                phase_spans.append((current_p, count))
                current_p = p
                count = 1
        phase_spans.append((current_p, count))

    # --- 2. BUILD THE EXACT EXCEL HTML TABLE (DATASET 1) ---
    st.markdown(
        """
    <style>
    :root {
        --tbl-bg: #ffffff;
        --tbl-text: #212529;
        --tbl-border: #e9ecef;
        --tbl-header-timeline: #2e7d32; 
        --tbl-header-phase: #d84315;    
        --tbl-header-text: #ffffff;
        --tbl-first-col: #f8f9fa;
        --tbl-row-hover: #f1f3f5;
        --tbl-cell-hover: #bbdefb;      
        --tbl-cell-hover-text: #000000;
        --tbl-first-col-hover: #e2e6ea;
    }

    @media (prefers-color-scheme: dark) {
        :root {
            --tbl-bg: #0E1117;
            --tbl-text: #FAFAFA;
            --tbl-border: #333333;
            --tbl-header-timeline: #2e7d32; 
            --tbl-header-phase: #d84315;    
            --tbl-header-text: #ffffff;
            --tbl-first-col: #262730;
            --tbl-row-hover: #1e1e24;
            --tbl-cell-hover: #1976d2;      
            --tbl-cell-hover-text: #ffffff;
            --tbl-first-col-hover: #333642;
        }
    }

    .excel-table { 
        border-collapse: collapse;
        width: 100%; 
        font-family: 'Source Sans Pro', sans-serif; 
        color: var(--tbl-text);
        background-color: var(--tbl-bg);
        border-radius: 8px;
        overflow: hidden;
        box-shadow: 0px 4px 12px rgba(0, 0, 0, 0.1); 
        margin-bottom: 20px;
    }
    .excel-table th, .excel-table td { 
        border: 1px solid var(--tbl-border); 
        padding: 12px 10px; 
        text-align: center; 
        transition: all 0.2s ease-in-out; 
    }
    .excel-table th { 
        font-weight: 600;
        color: var(--tbl-header-text);
    }
    .excel-table td:first-child { 
        text-align: left; 
        background-color: var(--tbl-first-col); 
        font-weight: 600;
    }
    .row-timeline th { background-color: var(--tbl-header-timeline) !important; }
    .row-phase th { background-color: var(--tbl-header-phase) !important; }
    .excel-table tr:hover td { background-color: var(--tbl-row-hover); }
    .excel-table td:hover {
        background-color: var(--tbl-cell-hover) !important; 
        color: var(--tbl-cell-hover-text) !important;
        cursor: crosshair; 
        transform: scale(1.02); 
        box-shadow: 0px 0px 8px rgba(0,0,0,0.2);
    }
    .excel-table tr:hover td:first-child {
        background-color: var(--tbl-first-col-hover) !important;
        cursor: default;
        transform: none;
        box-shadow: none;
    }
    </style>
    """,
        unsafe_allow_html=True,
    )

    html = "<table class='excel-table'>"

    html += "<tr class='row-timeline'><th>Timeline</th>"
    for t in raw_timeline_row:
        html += f"<th>{str(t).strip()}</th>"
    html += "</tr>"

    html += "<tr class='row-phase'><th>Components/Phase</th>"
    for phase, span in phase_spans:
        html += f"<th colspan='{span}'>{phase}</th>"
    html += "</tr>"

    for row in data_rows:
        component_name = row[0]
        data_vals = row[1:]

        filled_vals = []
        curr_val = 0
        for v in data_vals:
            if v not in ["", "-", "?", None]:
                curr_val = int(float(v))
            filled_vals.append(curr_val)

        html += f"<tr><td>{component_name}</td>"
        idx = 0
        for phase, span in phase_spans:
            val = filled_vals[idx]
            html += f"<td colspan='{span}'>{val}</td>"
            idx += span
        html += "</tr>"

    html += "</table>"
    st.markdown(html, unsafe_allow_html=True)

    # --- 3. LOGICAL DATAFRAME FOR CHARTS (DATASET 1: Test Completion) ---
    logical_columns = [("Timeline", "Components/Phase")]
    for t, p in zip(raw_timeline_row, filled_phases):
        logical_columns.append((str(t).strip(), p))

    logical_df = pd.DataFrame(data_rows)
    logical_df.columns = pd.MultiIndex.from_tuples(logical_columns)

    value_cols = logical_df.columns[1:]
    for col in value_cols:
        logical_df[col] = pd.to_numeric(
            logical_df[col].replace(["", "-", "?"], pd.NA), errors="coerce"
        )
    logical_df[value_cols] = logical_df[value_cols].ffill(axis=1).fillna(0)
    unique_phases = list(dict.fromkeys(filled_phases))
    component_list = logical_df[("Timeline", "Components/Phase")].tolist()

    # --- 3B. LOGICAL DATAFRAME FOR CHARTS (DATASET 2: Validation Confidence) ---
    raw_timeline_row_val = scope_validation_confidence[0][1:]
    raw_phase_row_val = scope_validation_confidence[1][1:]
    data_rows_val = scope_validation_confidence[2:]

    filled_phases_val = []
    current_phase_val = ""
    for phase in raw_phase_row_val:
        if phase and str(phase).strip() not in ["", "-", "?"]:
            current_phase_val = str(phase).strip()
        filled_phases_val.append(current_phase_val)

    logical_columns_val = [("Timeline", "Components/Phase")]
    for t, p in zip(raw_timeline_row_val, filled_phases_val):
        logical_columns_val.append((str(t).strip(), p))

    logical_df_val = pd.DataFrame(data_rows_val)
    logical_df_val.columns = pd.MultiIndex.from_tuples(logical_columns_val)

    value_cols_val = logical_df_val.columns[1:]
    for col in value_cols_val:
        logical_df_val[col] = pd.to_numeric(
            logical_df_val[col].replace(["", "-", "?"], pd.NA), errors="coerce"
        )
    logical_df_val[value_cols_val] = (
        logical_df_val[value_cols_val].ffill(axis=1).fillna(0)
    )
    unique_phases_val = list(dict.fromkeys(filled_phases_val))

    # --- 4. DROPDOWN CHART TRIGGER ---
    selected_component = st.selectbox(
        "Select a Component", ["-- Select --"] + component_list
    )

    # --- 5. COMPLETED VS REMAINING DONUT CHARTS (ALL IN ONE ROW) ---
    if selected_component != "-- Select --":

        # ==========================================
        # ROW 1: TEST COMPLETION STATUS
        # ==========================================
        st.subheader(
            f"EPVL - Test completion status for {selected_component} component",
            divider="blue",
        )

        phases_to_plot = unique_phases
        cols = st.columns(len(phases_to_plot))

        for i, phase in enumerate(phases_to_plot):
            with cols[i]:
                st.markdown(
                    f"<h4 style='text-align: center;'>{phase}</h4>",
                    unsafe_allow_html=True,
                )

                phase_columns = [col for col in logical_df.columns if col[1] == phase]

                if not phase_columns:
                    st.warning("No data")
                else:
                    comp_row = logical_df[
                        logical_df[("Timeline", "Components/Phase")]
                        == selected_component
                    ]

                    phase_vals = pd.to_numeric(
                        comp_row[phase_columns].iloc[0], errors="coerce"
                    ).fillna(0)
                    completed_val = int(phase_vals.max())

                    completed_val = max(0, min(100, completed_val))
                    remaining_val = 100 - completed_val

                    pie_df = pd.DataFrame(
                        {
                            "Status": ["Completed", "Remaining"],
                            "Percentage": [completed_val, remaining_val],
                        }
                    )

                    donut = (
                        alt.Chart(pie_df)
                        .mark_arc(innerRadius=45, stroke="transparent")
                        .encode(
                            theta=alt.Theta(field="Percentage", type="quantitative"),
                            color=alt.Color(
                                field="Status",
                                type="nominal",
                                scale=alt.Scale(
                                    domain=["Completed", "Remaining"],
                                    range=["#0864B4", "#b8a50f"],
                                ),
                                legend=None,
                            ),
                            tooltip=[
                                alt.Tooltip("Status", title="Status"),
                                alt.Tooltip("Percentage", title="   Value (%)"),
                            ],
                        )
                        .properties(height=250)
                    )

                    text = (
                        alt.Chart(pd.DataFrame({"text": [f"{completed_val}%"]}))
                        .mark_text(size=22, fontWeight="bold", color="#65B45C")
                        .encode(text="text:N")
                    )

                    final_chart = donut + text
                    st.altair_chart(final_chart, use_container_width=True)

        # st.divider() # Visual break between the two sections

        # ==========================================
        # ROW 2: VALIDATION CONFIDENCE
        # ==========================================
        st.subheader(
            f"EPVL - Validation Confidence for {selected_component} component",
            divider="blue",
        )

        phases_to_plot_val = unique_phases_val
        cols_val = st.columns(len(phases_to_plot_val))

        for i, phase in enumerate(phases_to_plot_val):
            with cols_val[i]:
                st.markdown(
                    f"<h4 style='text-align: center;'>{phase}</h4>",
                    unsafe_allow_html=True,
                )

                phase_columns_val = [
                    col for col in logical_df_val.columns if col[1] == phase
                ]

                if not phase_columns_val:
                    st.warning("No data")
                else:
                    comp_row_val = logical_df_val[
                        logical_df_val[("Timeline", "Components/Phase")]
                        == selected_component
                    ]

                    # If component doesn't exist in validation data, fallback to 0
                    if comp_row_val.empty:
                        completed_val_conf = 0
                    else:
                        phase_vals_conf = pd.to_numeric(
                            comp_row_val[phase_columns_val].iloc[0], errors="coerce"
                        ).fillna(0)
                        completed_val_conf = int(phase_vals_conf.max())

                    completed_val_conf = max(0, min(100, completed_val_conf))
                    remaining_val_conf = 100 - completed_val_conf

                    pie_df_val = pd.DataFrame(
                        {
                            "Status": ["Confidence", "Remaining"],
                            "Percentage": [completed_val_conf, remaining_val_conf],
                        }
                    )

                    donut_val = (
                        alt.Chart(pie_df_val)
                        .mark_arc(innerRadius=45, stroke="transparent")
                        .encode(
                            theta=alt.Theta(field="Percentage", type="quantitative"),
                            color=alt.Color(
                                field="Status",
                                type="nominal",
                                # Clean Teal (#00897B) and Gray (#6c757d) scheme for Confidence (Light/Dark mode compatible)
                                scale=alt.Scale(
                                    domain=["Confidence", "Remaining"],
                                    range=["#9EEE1C", "#ea550a"],
                                ),
                                legend=None,
                            ),
                            tooltip=[
                                alt.Tooltip("Status", title="Status"),
                                alt.Tooltip("Percentage", title="   Value (%)"),
                            ],
                        )
                        .properties(height=250)
                    )

                    text_val = (
                        alt.Chart(pd.DataFrame({"text": [f"{completed_val_conf}%"]}))
                        .mark_text(
                            size=22,
                            fontWeight="bold",
                            color="#00897B",  # Matches the teal
                        )
                        .encode(text="text:N")
                    )

                    final_chart_val = donut_val + text_val
                    st.altair_chart(final_chart_val, use_container_width=True)

    # # B. Samples requested Table and Bar chart
    # st.subheader("Test Samples requested data")
    # scope_sample_requested = dashb.fetch_horizontal_table(4, 19, 7, 16)
    # # 1. Define the column names based on your image's multi-level structure
    # column_names = [
    #     "Components/Phase",
    #     "Alpha P1 Requested",
    #     "Alpha P1 Delivered",
    #     "Alpha P2 Requested",
    #     "Alpha P2 Delivered",
    #     "Beta Requested",
    #     "Beta Delivered",
    #     "T0 Requested",
    #     "T0 Delivered",
    # ]  # creating the dataframe with column names
    # # 2. Convert  to a pandas DataFram
    # df = pd.DataFrame(scope_sample_requested, columns=column_names)

    # # 3. Clean the data , replacing junk with number  0 for plotting bar graph
    # df = df.replace(["", "-", "?", None], 0)

    # # 4. Set the index to the 'Components/Phase' column
    # df = df.set_index("Components/Phase")

    # # 5. Convert all data columns to numeric (forces any remaining hidden strings to NaN, then fills with 0)
    # df = df.apply(pd.to_numeric, errors="coerce").fillna(0)

    # filtered_df_allsamples = df  # displayes the dataframe with all coulmns
    # # --------------------------------------------------
    # # Define available samples
    # phases = ["Alpha P1", "Alpha P2", "Beta", "T0", "All"]

    # # Display the filtered dataframe
    # st.dataframe(filtered_df_allsamples)

    # # Create a dropdown for the user to select the sample type
    # st.subheader(f"Samples Requested vs Delivered Data (in days)")
    # selected_phase = st.selectbox("Select sample type:", phases)
    # # st.subheader(f"Samples Requested vs Delivered ({selected_phase})")

    # # Filter the DataFrame columns based on selection
    # if selected_phase == "All":
    #     filtered_df = df  # Show everything
    # else:
    #     # Keep only columns that contain the selected phase name
    #     columns_to_keep = [col for col in df.columns if selected_phase in col]
    #     filtered_df = df[columns_to_keep]

    # # Render the bar chart with the filtered data
    # st.bar_chart(filtered_df, horizontal=True)

    # # ######################################################
    # # 3 Graph
    # #st.subheader("Estimated Components Test Completion Time")

    # # Fetch data
    # scope_sample_timline = dashb.fetch_horizontal_table(4, 19, 17, 24)
    # columns_timeline = [
    #     "Components/Phase",
    #     "Alpha P1",
    #     "Alpha P2",
    #     "Beta",
    #     "T0",
    #     "SOP",
    #     "Test Closure",
    # ]

    # weeks_order = [
    #     "Nov Week 4",
    #     "Dec Week 1",
    #     "Dec Week 2",
    #     "Dec Week 3",
    #     "Dec Week 4",
    #     "Jan Week 1",
    #     "Jan Week 2",
    #     "Jan Week 3",
    #     "Jan Week 4",
    #     "Feb Week 1",
    # ]

    # df2 = pd.DataFrame(scope_sample_timline, columns=columns_timeline)
    # # --- 1. CLEAN COMPONENTS AND SET HARDCODED VALUES ---
    # # Remove the header row if it accidentally got pulled as data
    # df2 = df2[df2["Components/Phase"] != "Components/Phase"]

    # # Strip hidden spaces from Component names and drop completely empty rows
    # df2["Components/Phase"] = df2["Components/Phase"].astype(str).str.strip()
    # df2 = df2[df2["Components/Phase"] != ""]
    # df2 = df2[df2["Components/Phase"] != "None"]

    # # Hardcode T0 to "Nov Week 4" for all components
    # df2["T0"] = "Nov Week 4"

    # # Replace any empty strings or hyphens in Test Closure with "TBD"
    # df2["Test Closure"] = df2["Test Closure"].replace(
    #     ["", "-", "None", "nan", None], "TBD"
    # )

    # # --- 2. DISPLAY CLEAN TABLE ---
    # # st.dataframe(df2.set_index('Components/Phase'))

    # # --- 3. PREPARE SPLIT DATA FOR CHART ---
    # df_chart = df2.copy()

    # # Get a definitive list of ALL components to force the Y-axis to render them
    # all_components = df_chart["Components/Phase"].unique().tolist()

    # # Map weeks to numerical indexes
    # week_idx = {week: i for i, week in enumerate(weeks_order)}
    # sop_week = "Jan Week 4"
    # sop_idx = week_idx[sop_week]

    # # --- THE LOGIC FIX ---
    # # If Test Closure is "TBD" (not in week_idx), force the bar to stop at SOP ("Jan Week 4")
    # df_chart["Test Closure"] = df_chart["Test Closure"].apply(
    #     lambda x: x if x in week_idx else sop_week
    # )

    # # Logic to split bars exactly at the SOP line
    # segments = []
    # for _, row in df_chart.iterrows():
    #     comp = row["Components/Phase"]
    #     t0 = row["T0"]
    #     tc = row["Test Closure"]

    #     tc_index = week_idx[tc]

    #     # If the test finishes BEFORE or ON the SOP week
    #     if tc_index <= sop_idx:
    #         segments.append(
    #             {"Component": comp, "Start": t0, "End": tc, "Status": "Before SOP"}
    #         )

    #     # If the test spans ACROSS the SOP line
    #     else:
    #         segments.append(
    #             {
    #                 "Component": comp,
    #                 "Start": t0,
    #                 "End": sop_week,
    #                 "Status": "Before SOP Deadline",
    #             }
    #         )
    #         segments.append(
    #             {
    #                 "Component": comp,
    #                 "Start": sop_week,
    #                 "End": tc,
    #                 "Status": "After SOP Deadline",
    #             }
    #         )

    # df_segments = pd.DataFrame(segments)

    # # --- 4. ALTAIR CHART ---

    # # Draw the split Gantt bars
    # gantt_bars = (
    #     alt.Chart(df_segments)
    #     .mark_bar(height=15, cornerRadius=2)
    #     .encode(
    #         x=alt.X(
    #             "Start:O",
    #             sort=weeks_order,
    #             scale=alt.Scale(domain=weeks_order),
    #             axis=alt.Axis(values=weeks_order),
    #             title="Timeline (Weeks)",
    #         ),
    #         x2=alt.X2("End:O"),
    #         y=alt.Y(
    #             "Component:N",
    #             title="Components",
    #             sort=all_components,
    #             scale=alt.Scale(domain=all_components),
    #         ),
    #         color=alt.Color(
    #             "Status:N",
    #             scale=alt.Scale(
    #                 domain=["Before SOP", "After SOP"],
    #                 range=["#1976d2", "#ff7f0e"],  # Blue for before, Orange for after
    #             ),
    #             title="SOP Deadline",
    #         ),
    #     )
    # )
    # # Draw the Singular Standard SOP Line at Jan Week 4
    # sop_standard_line = (
    #     alt.Chart(pd.DataFrame({"SOP_DeadLine": [sop_week]}))
    #     .mark_rule(color="red", strokeDash=[5, 5], strokeWidth=2)
    #     .encode(x=alt.X("SOP_DeadLine:O", sort=weeks_order))
    # )

    # st.markdown("Estimated completion time of Individiual components")
    # # Combine and display
    # final_timeline_chart = (gantt_bars + sop_standard_line).properties(
    #     width=700, height=400
    # )
    # st.altair_chart(final_timeline_chart, use_container_width=True)
