import pandas as pd


class Xlsx:
    def __init__(self, path: str):
        self.path = path
        self.file = pd.ExcelFile(path)
        self.sheets = {}

    def _sync_sheet(self, name: str):
        if name not in self.sheets:
            self.sheets[name] = pd.read_excel(
                self.file, name, index_col="Timestamp")

    def get_sheet(self, name: str):
        self._sync_sheet(name)
        return self.sheets[name]

    def get_sheets(self):
        for sheet_name in self.get_sheets_names():
            self._sync_sheet(sheet_name)
        return self.sheets

    def get_sheets_names(self):
        return self.file.sheet_names

    def get_sheet_columns_names(self, name: str):
        self._sync_sheet(name)
        return self.sheets[name].columns
