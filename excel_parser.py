from pandas import read_excel


class ExcelParse:
    def __init__(self, file, sheet):
        self.xlfile = read_excel(file, sheet)

    def fetch_coloumn_values(self, coloumn_name, list):
        if list:
            return self.xlfile[coloumn_name].to_list()
        return self.xlfile.columns.values


# throttle_df_list = throttle_df['auth_code'].tolist()
# samp = throttle_df['vcu_public_key'].tolist()
