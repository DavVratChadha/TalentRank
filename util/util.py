import csv
import pandas as pd


#function to read csv file
def read_csv(file_path):
    with open(file_path, 'r') as file:
        reader = csv.reader(file)
        data = list(reader)
    return data

#function to turn xlsx to csv
def xlsx_to_csv(file_path, new_name):
    import pandas as pd
    data_xls = pd.read_excel(file_path, index_col=None)
    data_xls.to_csv(new_name, encoding='utf-8')


#function to load csv as dataframe
def load_csv_as_df(file_path):
    return pd.read_csv(file_path)
