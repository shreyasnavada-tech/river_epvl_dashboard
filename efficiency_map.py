import os
import sys
from typing import Any

import pandas as pd
from pandas.io.formats.style import Styler

# Spectrum from red to yellow to green
colour_list = [
    "00FF0000",
    "00FFA000",
    "00ffC000",
    "00ffe000",
    "00ffff00",
    "00e0ff00",
    "00c0ff00",
    "00a0ff00",
    "0000FF00",
]


def extract_csv(file: str) -> pd.DataFrame:
    return pd.read_csv(file)


def get_min_max_values_in_df(data_frame: pd.DataFrame) -> tuple[list, list]:
    min_val_list = []
    max_val_list = []
    for col_name in data_frame.columns.to_list():
        min_val_list.append(data_frame[col_name].min().tolist())
        max_val_list.append(data_frame[col_name].max().tolist())
    return min_val_list[1:], max_val_list[1:]


def get_max_min_value_from_list(val_list: list, lim_type: str) -> Any:
    if lim_type == "max":
        return max(val_list)
    return min(val_list)


# Refer https://matplotlib.org/stable/users/explain/colors/colormaps.html for cmap values
def style_df(
    data_frame: pd.DataFrame, cmap: str, value_range: list = [50, 101]
) -> Styler:
    return data_frame.style.background_gradient(
        cmap=cmap,
        vmin=value_range[0],
        vmax=value_range[1],
        subset=pd.IndexSlice[:, csv_data.columns != "Speed"],
    )


if __name__ == "__main__":
    # Pass the path of the folder where the csv files are located
    # Ex: python efficiency_map.py /Users/nagendrar/Downloads/CommonReport /Users/nagendrar/Desktop
    folder_name = sys.argv[1]
    dest_name = sys.argv[2]

    # Defined paths only work on Unix systems
    with pd.ExcelWriter(
        f"{dest_name}/efficiency_map.xlsx", engine="openpyxl"
    ) as writer:
        for file in os.listdir(folder_name):
            file_name = file.split(".")[0]
            csv_data = extract_csv(f"{folder_name}/{file_name}.csv")
            # Increase input range to get better grads but lesser colour changes
            min_df, max_df = get_min_max_values_in_df(csv_data)
            min_value = get_max_min_value_from_list(min_df, "min")
            max_value = get_max_min_value_from_list(max_df, "max")
            sh_name = file_name.split("_")
            style_df(csv_data, "RdYlGn", [min_value, max_value]).to_excel(
                writer,
                sheet_name=sh_name[1] + sh_name[2] if len(sh_name) == 3 else sh_name[1],
                index=False,
            )
