import io
import os
import pandas as pd
from date_parsers import custom_knmi_date_parser, date_parser, factoryzero_date_parser, knmi_date_parser


def parse_csv(buffer: bytes, index_column: str, separator: str = ',') -> pd.DataFrame:
    data = io.StringIO(buffer.decode('utf-8'))
    return pd.read_csv(data, sep=separator, index_col=index_column,
                       converters={index_column: date_parser})


def parse_xlsx(buffer: bytes, index_column: str, sheet_name: str) -> pd.DataFrame:
    return pd.read_excel(buffer, sheet_name=sheet_name, index_col=index_column,
                         converters={index_column: factoryzero_date_parser})


def parse_uploaded_file(filename: str, buffer: bytes, index_column: str, column_to_impute: str, sheet_name: str = None, start_timestamp: int = None, end_timestamp: int = None) -> pd.DataFrame:
    ext = os.path.splitext(filename)[1][1:]
    if ext == 'csv':
        df = parse_csv(buffer, index_column)
    elif ext == 'xlsx':
        assert sheet_name != None
        df = parse_xlsx(buffer, index_column, sheet_name)
    else:
        raise Exception(f'Unsupported file extension: {ext}')

    columns_to_drop = [it for it in df.columns.drop(column_to_impute)]
    df.drop(columns=columns_to_drop, inplace=True)

    if start_timestamp != None:
        df = df[df.index >= start_timestamp]
    if end_timestamp != None:
        df = df[df.index <= end_timestamp]

    return df
