import gc
import io
import os
import time
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from logging import Logger
from typing import Any, List, Optional

import numpy as np
import pandas as pd
import polars as plr
import psutil
import pyarrow as pa

# from .dbc_parser_pt import DBCParser
from dbc_parser_pt import DBCParser
from nptdms import TdmsFile
from pandas import DataFrame, Series


@dataclass
class DataParser:
    """
    Base class with methods to parse data in a csv file. Uses a Dataframe object for further processing
    """

    dtframe: DataFrame

    def get_coloumn_name_list(self) -> list:
        """
        The method returns the list of coloumns present in the DF
        """
        self.coloumn_list = self.dtframe.columns
        return self.coloumn_list.to_list()

    @staticmethod
    def coloumn_width() -> Any:
        """
        This method gets the coloumns width used for display

        Return:
            The coloumn width used in display
        """
        return pd.get_option("display.max_columns")

    @staticmethod
    def set_coloumn_width(len: Optional[int] = 500):
        """
        This is setter for coloumn width

        Args:
            len: int = Length of the coloumns used for display
        """
        pd.set_option("display.max_columns", len)

    def get_max_value_coloumn(self, coloumn_name: str) -> Any:
        """
        This method returns the max value in the given coloumn

        Args:
            coloumn_name: str = Name of the coloumn

        Returns:
            max_value: Any
        """
        return self.dtframe.columns[coloumn_name].max()

    def get_row_data(self, row_number: int) -> Series:
        """
        The method returns the data in the row for a given row number.
        Lets say there are 10 rows and the data in the 3rd row is needed, we need to
        to select 3-1 as the value of the length

        Args:
            row_number: int = row_number is n-1 of the row to be displayed

        Returns:
            A Pandas series frame consisting of the row data
        """
        return self.dtframe.iloc[row_number]

    def get_multiple_row_data(self, n_rows: tuple[int, list]) -> DataFrame:
        """
        This method extracts multiple row data in a given DF

        Args:
            n_rows: tuple[int, list] = If the value is an int: Extract 0 till int value data
                                       i.e if int value is 4, extract 0 to 4th row data
                                       If the value is a list in the following format [Starting index: Ending index],
                                       slice the row values between the indices.
                                       If value is [1,5], extract values between 1st and 5th row including 1st and 5th

        Returns:
            A Dataframe consisting of the extracted row data
        """
        if isinstance(n_rows, list):
            return self.dtframe.loc[n_rows[0] : n_rows[1]]
        return self.dtframe.loc[slice(0, n_rows)]

    def get_coloumn_data(self, col_name: str) -> Series:
        """
        This method returns the data for the requested coloumn name

        Args:
            col_name: str = Name of the coloumn

        Returns:
            A Pandas series coloumn data
        """
        return self.dtframe.get(col_name)

    def get_multiple_coloumn_data(self, col_name_list: list[str]) -> DataFrame:
        """
        This method provides the data for select coloumns

        Args:
            col_name_list: list[str] = Coloumn names for which data is needed. Ex - ['col_1', 'col_2']

        Returns:
            A dataframe for the selected coloumns' data
        """
        return self.dtframe.loc[:, col_name_list]

    def get_n_rows(self, n_rows: int) -> DataFrame:
        """
        This method provides row data till the nth row

        Args:
            n_rows: int = Row number till where the DF is needed.

        Returns:
            A DF with the required row data
        """
        return self.dtframe.head(n_rows)

    def check_value_in_df(self, value: Any) -> bool:
        """
        This method checks if a particular value is present in the complete dataframe

        Args:
            value: Any = The value to be found in the DF

        Returns:
            A Boolean value indicating if the value is present in the DF
        """
        if value in self.dtframe.values:
            return True
        return False

    def coloumn_name_in_df(self, col: str) -> bool:
        """
        This method check if a coloumn name is present in the dataframe

        Args:
            col: str = The coloumn name to be checked

        Returns:
            A Boolean value indicating if the coloumn name is present in the DF
        """
        return col in self.dtframe.columns

    @staticmethod
    def check_value_in_series(series: Series, value: Any) -> bool:
        """
        This method checks if a certain value is present in the series.

        Args:
            series: Series = Series data of row/coloumn
            value: Any = Value to be found in the series

        Returns:
            A Boolean value indicating if the value is present in the DF
        """
        return True if value in series.values else False

    def get_conditional_equality_row_data(
        self, key: Any, value: Any, condition: Any
    ) -> Series:
        """
        This method obtains all the rows that match the key and the value in the form of a list

        Args:
            key: Any = Key to be used
            value: Any = Value to be compared
            condition: optr = Condition obtained from the Operator module.
                              It supports the following -
                                operator.lt(a, b) - Less than
                                operator.le(a, b) - Less than or equal to
                                operator.eq(a, b) - Equal to
                                operator.ne(a, b) - Not equal to
                                operator.ge(a, b) - Greater than
                                operator.gt(a, b) - Greater than or equal to

                               Pass in optr.condition as listed above
        Returns:
            A list with all the rows that satisfy the condition
        """
        series_data = []
        for index, frame in self.dtframe.iterrows():
            if condition(frame[key], value):
                series_data.append(frame)

        return series_data

    def get_specific_value_in_row_coloumn_pair(
        self, row_num: int, col_name: str
    ) -> Any:
        """
        This method gets value of a certain cell if the row number and the coloumn name are mentioned

        Args:
            row_num: int = Row number
            col_name: str = Name of the coloumn

        Returns:
            The value of the requested cell
        """
        return self.dtframe.at[row_num, col_name]

    def set_specific_value_in_row_coloumn_pair(
        self, row_num: int, col_name: str, value: Any
    ) -> Any:
        """
        This method sets value of a certain cell if the row number and the coloumn name are mentioned

        Args:
            row_num: int = Row number
            col_name: str = Name of the coloumn
            value: Any = Value to be set at the given cell

        Returns:
            The value of the cell after setting the value
        """
        self.dtframe.at[row_num, col_name] = value
        return f"Value set is {self.get_specific_value_in_row_coloumn_pair(row_num, col_name)}"

    @staticmethod
    def convert_df_to_pythonic_data_types(
        df: DataFrame, data_type: str
    ) -> tuple[list, dict]:
        """
        This method converts the input date frame into list or dict based on argument

        Args:
            df: DataFrame - A standard Pandas Dataframe
            datatype: str = One of 'list' or 'dict'

        Returns:
            A dict or list
        """
        match data_type:
            case "list":
                return df.values.tolist()
            case "dict":
                return df.to_dict("dict")
            case _:
                raise ValueError(
                    f"The requested data type conversion is not supported. Please provide one of `list` or `dict`."
                )

    def filter_coloumn_data_on_condition(
        self, mask: Any, addtional_coloumns: Optional[tuple[str, list]]
    ) -> DataFrame:
        """
        This method provides a subset of the coloumn values based on the mask. The requested mask is applied for a given coloumn and
        other coloumns under the mask condition can also be obtained

        Args:
            mask: Any = Condition under which the values of the coloumn needs to be looked into
            addtional_coloumns: tuple[str, list] = If additional coloumns need to be extracted, a single coloumn name as string or a list of coloumn names
            can be provided. If None, only the masked coloumn will be parsed
            Ex:
                'col1' or ['col1', 'col2']

        Returns:
            Masked coloumn data and addtional coloumns if requested
        """
        if addtional_coloumns is not None:
            return self.dtframe.loc[mask, addtional_coloumns]
        return self.dtframe.loc[mask]


class TDMS_file_handler:

    def __init__(self, tdms_path: str):
        self.file_path = os.path.abspath(tdms_path)

        # 1. FIX THE PARSING ERROR (Index Repair)
        index_path = self.file_path + "_index"
        if os.path.exists(index_path):
            try:
                os.remove(index_path)
                print("Corrupt index detected and removed. Rebuilding at high speed...")
            except Exception as e:
                print(f"Note: Could not delete index (file may be in use): {e}")

        # 2. HARDWARE ASCENSION
        p = psutil.Process(os.getpid())
        if os.name == "nt":
            p.nice(psutil.REALTIME_PRIORITY_CLASS)

        # 3. OPEN WITH FRESH INDEX
        # We use 'read' here to ensure the index is fully mapped before the workers start
        self.tdms_obj = TdmsFile.read(self.file_path)

    @staticmethod
    def _fill_buffer(args):
        """DSA: Lowest-overhead memory write."""
        channel_obj, target_buffer = args
        # read_data() is the C-extension accessor. It bypasses the parsing error logic.
        data = channel_obj.read_data()
        target_buffer[: len(data)] = data

    def convert_tdms_to_df(self) -> pd.DataFrame:
        # print(
        #     f"--- Hard-Core Robust Extraction: {os.path.basename(self.file_path)} ---"
        # )
        start_time = time.time()
        gc.disable()

        try:
            # 1. METADATA SCAN (Now fast because index is fixed)
            all_channels = [
                chan for group in self.tdms_obj.groups() for chan in group.channels()
            ]
            max_rows = max(len(c) for c in all_channels)
            num_channels = len(all_channels)
            col_names = [f"{c.group_name}/{c.name}" for c in all_channels]

            # 2. DSA: PRE-ALLOCATED CONTIGUOUS BLOCK (Fortran Order)
            # print(f"Pre-allocating Buffer: {num_channels} cols x {max_rows} rows")
            master_buffer = np.full(
                (num_channels, max_rows), np.nan, dtype=np.float32, order="F"
            )

            # 3. PARALLEL BUFFER FILLING (24 Workers)
            extract_tasks = [
                (all_channels[i], master_buffer[i]) for i in range(num_channels)
            ]

            print(f"Streaming data via 24 workers...")
            with ThreadPoolExecutor(max_workers=24) as executor:
                list(executor.map(self._fill_buffer, extract_tasks))

            extraction_end = time.time()
            print(f"I/O Stream finished in {extraction_end - start_time:.2f}s.")

            # 4. ZERO-COPY ARROW HANDOFF
            # Bridge to Arrow to bypass the Pandas 'BlockManager' delay
            data_dict = {col_names[i]: master_buffer[i] for i in range(num_channels)}
            table = pa.Table.from_pydict(data_dict)

            del master_buffer
            del data_dict

            # 5. INSTANT PANDAS CONVERSION (Arrow Backend)
            df = table.to_pandas(
                types_mapper=pd.ArrowDtype, self_destruct=True, split_blocks=True
            )

        finally:
            gc.enable()

        total_time = time.time() - start_time
        print(f"--- TOTAL TIME: {total_time:.2f} Seconds ---")
        return df

    @staticmethod
    def convert_df_to_excel(df: DataFrame, name: str, index: bool = False):
        """
        This method converts tdms into excel with or without index

        Args:
            name: str = Name of the file to be generated
            index: False = If True = index is added
                            Else, no index in excel
        """
        return df.to_excel(name, index=index)

    @staticmethod
    def convert_df_to_csv(df: DataFrame, name: str, index: bool = False):
        """
        This method converts tdms into csv with or without index

        Args:
            name: str = Name of the file to be generated
            index: False = If True = index is added
                            Else, no index in csv
        """
        return df.to_csv(name, index=index)


class BMaster_XLS_Parser:
    """
    Docstring for BMaster_XLS_Parser

    This class tries to parse data in .Log file generated by Busmaster
    Sample data -

    ***BUSMASTER Ver 3.2.2
    ***PROTOCOL CAN***
    ***NOTE: PLEASE DO NOT EDIT THIS DOCUMENT***
    ***[START LOGGING SESSION]***
    ***START DATE AND TIME 2:2:2026 16:49:37:325***
    ***HEX***
    ***SYSTEM MODE***
    ***START CHANNEL BAUD RATE***
    ***CHANNEL 1 - PCAN-USB Driver Id 16 - 500000 bps***
    ***END CHANNEL BAUD RATE***
    ***START DATABASE FILES***
    ***END DATABASE FILES***
    ***<Time><Tx/Rx><Channel><CAN ID><Type><DLC><DataBytes>***
    16:49:37:3329 Rx 1 0x144 s 8 5E 2C 00 00 00 10 04 00
    16:49:37:3349 Rx 1 0x145 s 8 E4 61 1D 00 00 00 22 05
    16:49:37:3389 Rx 1 0x142 s 8 41 00 00 80 00 60 00 00
    16:49:37:3403 Rx 1 0x146 s 8 05 28 40 15 00 00 00 08
    16:49:37:3408 Rx 1 0x143 s 8 00 10 E0 BF 11 00 00 00
    16:49:37:3428 Rx 1 0x144 s 8 5E 2C 00 00 00 10 04 00
    16:49:59:7723 Rx 1 0x700 s 8 56 19 0C 04 01 AA 02 43
    16:49:59:7726 Rx 1 0x237 s 6 03 00 FF FF FF FF
    16:49:59:7731 Rx 1 0x241 s 8 00 00 00 00 00 E8 03 00
    16:49:59:7733 Rx 1 0x148 s 5 40 E4 90 C0 00
    16:49:59:7736 Rx 1 0x24A s 8 00 01 00 00 00 00 00 00
    16:49:59:7739 Rx 1 0x24B s 8 00 00 00 00 00 00 00 00
    ***END DATE AND TIME 2:2:2026 16:50:0:39***
    ***[STOP LOGGING SESSION]***

    file_name: str = Nam of the .Log file
    """

    def __init__(self, file_name: str):
        self.file = file_name

    def get_df(self):
        """Get the Dataframe in the current state"""
        return self.df

    def read_file_into_memory(self):
        """
        This method reads file generated from BUSMASTER: .Log file into memory
        """
        NON_DATA_STRING_LINES_AT_START_OF_FILE = 14
        NON_DATA_STRING_LINES_AT_END_OF_FILE = -4
        with open(self.file) as f:
            self.raw_data = f.readlines()
            self.filtered_data = self.raw_data[
                NON_DATA_STRING_LINES_AT_START_OF_FILE:NON_DATA_STRING_LINES_AT_END_OF_FILE
            ]

    def generate_dataframe(self):
        """
        This method generates dataframe from data provided by read_file_into_memory() method
        """
        # Setting str as datatype for
        dtype_map = {
            "Byte0": str,
            "Byte1": str,
            "Byte2": str,
            "Byte3": str,
            "Byte4": str,
            "Byte5": str,
            "Byte6": str,
            "Byte7": str,
        }

        # Since the coloumn names are removed from .Log file, we need to add coloumn names back into the frame.
        coloumn_names = [
            "time",
            "_tx",
            "_rx",
            "hex_id",
            "_s",
            "_length",
            "Byte0",
            "Byte1",
            "Byte2",
            "Byte3",
            "Byte4",
            "Byte5",
            "Byte6",
            "Byte7",
        ]

        # Reading the .Log file with the coloumn names
        self.df = pd.read_csv(
            io.StringIO("\n".join(self.filtered_data)),
            sep=r"\s+",
            names=coloumn_names,
            converters=dtype_map,
        )
        return self.df

    def merge_data_coloumns_into_df(self):
        """
        This method concatenates all bytes into one byte:
        Byte0 Byte1 Byte2 Byte3 Byte4 Byte5 Byte6 Byte7                     Data
        5E    2C    00    00    00    10    04    00                5E 2C 00 00 00 10 04 00
        E4    61    1D    00    00    00    22    05                E4 61 1D 00 00 00 22 05
        41    00    00    80    00    60    00    00                41 00 00 80 00 60 00 00
        """
        self.df["raw_data"] = self.df["Byte0"].str.cat(
            [
                self.df["Byte1"],
                self.df["Byte2"],
                self.df["Byte3"],
                self.df["Byte4"],
                self.df["Byte5"],
                self.df["Byte6"],
                self.df["Byte7"],
            ],
            sep=" ",
        )
        self.data = self.df["raw_data"]

    def drop_coloumns(
        self,
        coloumn_list: List = [
            "_tx",
            "_rx",
            "_s",
            "_length",
            "Byte0",
            "Byte1",
            "Byte2",
            "Byte3",
            "Byte4",
            "Byte5",
            "Byte6",
            "Byte7",
        ],
    ):
        """
        This method drops coloumns provided as a list
        """
        self.df.drop(columns=coloumn_list, inplace=True)

    def generate_filtered_df(self):
        """
        Apart from using all methods, it changes data type of Data coloumn into a list of hex values and removes 0x from the CAN IDs
        """
        self.read_file_into_memory()
        self.generate_dataframe()
        self.merge_data_coloumns_into_df()
        self.drop_coloumns()

        try:
            self.df["decimal_id"] = self.df["hex_id"].apply(
                lambda x: int(x.split("x")[1], 16)
            )
        except Exception as e:
            print(e)
        # Convert a string into a list
        # 5E 2C 00 00 00 10 04 00 into [5E, 2C, 00, 00, 00, 10, 04, 00]

        self.df["raw_data"] = self.df["raw_data"].apply(
            lambda x: self.convert_str_into_hex_values(x)
        )
        return self.df

    @staticmethod
    def convert_str_into_hex_values(value):
        """Convert list of strings into a list of hex values"""
        return [int(val, 16) for val in value.split()]


class TRC_Filehandler:
    def __init__(self, file: str, dbc_file):
        self.file = file
        self.dbc_file = dbc_file
        self.polars_df = None

    # def read_csv_to_polars(self, skip_rows: int, separator: str = ' ', has_header=False, ignore_errors=True, truncate_ragged_lines=True):
    def read_csv_to_polars(
        self,
        skip_rows: int,
        separator: str = " ",
        has_header=False,
        ignore_errors=True,
        truncate_ragged_lines=True,
    ):
        # Second method to try - scan csv or use lazt csv

        # 1. Read the File
        df = plr.read_csv(
            self.file,
            skip_rows=skip_rows,
            separator="\x1e",
            has_header=False,
            ignore_errors=ignore_errors,
            truncate_ragged_lines=truncate_ragged_lines,
        )

        col_name = df.columns[0]

        # 2. Extract groups via Regex
        pattern = r"^\s*(?<index>\d+)\)\s+(?<time>[\d\.]+)\s+(?<direction>\w+)\s+(?<hex_id>[A-Fa-f0-9]+)\s+(?<dlc>\d+)\s+(?<raw_data>.*?)\s*$"

        self.polars_df = (
            df.select(plr.col(col_name).str.extract_groups(pattern).alias("fields"))
            .unnest("fields")
            .drop_nulls()
        )

        # 3. Cast and Convert
        self.polars_df = self.polars_df.with_columns(
            [
                plr.col("index").cast(plr.Int64),
                plr.col("time").cast(plr.Float64),
                plr.col("hex_id").str.to_integer(base=16).alias("decimal_id"),
                plr.col("raw_data")
                .str.split(" ")
                .list.eval(plr.element().str.to_integer(base=16))
                .alias("raw_signal_data"),
            ]
        )

        # 4. PRE-FILTER: Match IDs in DBC
        try:
            valid_ids = [msg.frame_id for msg in self.dbc_file.db.messages]
            Logger.info(valid_ids)
            self.polars_df = self.polars_df.filter(
                plr.col("decimal_id").is_in(valid_ids)
            )
            Logger.info(self.polars_df)
            Logger.info("Prefilter applied")
        except Exception:
            pass
        # --- STEP 5: Create a Unique Lookup Table ---
        # Instead of 65M rows, we likely only have a few thousand UNIQUE messages.
        # We use the 'raw_data' string as a key because joining on strings is faster than lists.
        unique_messages = self.polars_df.select(["decimal_id", "raw_data"]).unique()

        # --- STEP 6: High-Speed Unique Decoding ---
        def decode_payload(msg_id, raw_hex_str):
            try:
                # Convert hex string back to bytes for the decoder
                payload_bytes = bytes.fromhex(raw_hex_str.replace(" ", ""))
                decoded = self.dbc_file.decode_message(msg_id, payload_bytes)
                # Return an empty dict instead of None to keep from_dicts happy
                return decoded if decoded else {}
            except:
                return {}

        # Decode only the unique subset (this should be very fast)
        decoded_list = [
            decode_payload(row[0], row[1]) for row in unique_messages.iter_rows()
        ]

        # Create the lookup dataframe
        lookup_table = plr.from_dicts(decoded_list)

        lookup_df = plr.concat([unique_messages, lookup_table], how="horizontal")

        # --- STEP 7: The "Big Join" ---
        self.polars_df = self.polars_df.join(
            lookup_df, on=["decimal_id", "raw_data"], how="left"
        )

        return self.polars_df


if __name__ == "__main__":
    # print(True)
    dbc_parser = DBCParser(
        dbc_name=r"C:\Users\shreyasnavada_rideri\Documents\dev\vehicle-automation\motor_dyno_webapp\Data\DBC_Gen2_3_V1_7 09-02-2025 E_PVLatest.dbc"
    )
    """
    Test TRC file for data frame creation
    """
    # trcfilepath = r"C:\Users\shreyasnavada_rideri\Documents\dev\vehicle-automation\motor_dyno_webapp\Data\testTRC.trc"
    trcfile = TRC_Filehandler(
        r"C:\Users\shreyasnavada_rideri\Documents\dev\vehicle-automation\motor_dyno_webapp\Data\testTRC_5linestest.trc",
        dbc_parser,
    )
    # trcfile = TRC_Filehandler(r"C:\Users\shreyasnavada_rideri\Documents\dev\vehicle-automation\motor_dyno_webapp\Data\20260302.trc", dbc_parser)
    start_time = time.perf_counter()
    df_polars_trc = trcfile.read_csv_to_polars(20)
    print(df_polars_trc.glimpse())
    end_time = time.perf_counter()
    time1 = end_time - start_time
    print(f"total time taken for Polars Dataframe creation  is {time1}")

    # df = pd.read_csv("/Users/nagendrar/Documents/river_dev/vehicle-automation/utility_scripts/grpc-server-client/Gen2_sample.csv")
    # dp = DataParser(df)
    # print(repr(dp), str(dp))
    # print(dp.get_row_data(1))
    # print(dp.check_value_in_series(dp.get_row_data(1), 'CCCV Chg'))
    # print(dp.get_coloumn_data('Cycle Index'))
    # print(dp.get_multiple_coloumn_data(['Cycle Index', 'Step Time']))
    # print(dp.get_n_rows(3))
    # print(dp.get_multiple_row_data(2))
    # print(dp.get_coloumn_name_list())
    # print(dp.coloumn_width)
    # dp.coloumn_width = 23
    # print(dp.coloumn_width)
    # # print(dp.check_value_in_df(""))
    # print(dp.coloumn_name_in_df("Step Time"))
    # print(dp.get_conditional_equality_row_data("Step Number", 3, optr.gt))
    # a = TDMS_file_handler("tester.tdms")
    # b = a.convert_tdms_to_df(False)
    # print(b)
    # a.convert_df_to_excel(b, "sample.xlsx")
    # a.convert_df_to_csv(b, "a.csv")
    # a = BMaster_XLS_Parser(
    #     r"C:\Users\shreyasnavada_rideri\Documents\dev\vehicle-automation\motor_dyno_webapp\Data\VIN_9998_501_issue.log"
    # )
    # print(a.generate_filtered_df())

    # b = TDMS_file_handler(
    #     r"C:\Users\shreyasnavada_rideri\Documents\dev\vehicle-automation\motor_dyno_webapp\Data\TestFileTDMS3.tdms"
    # )
    # print(b.tdms_file)
    # c = b.convert_tdms_to_df()
    # print("test file " +c)
