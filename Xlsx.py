import pandas as pd


class Xlsx:
    __current_idx = 0

    def __init__(self, path: str):
        self.path = path
        self.file = pd.ExcelFile(path)
        self.sheets = {}

    def __iter__(self):
        return self

    def __next__(self):
        if (self.__current_idx >= len(self.file.sheet_names)):
            raise StopIteration
        sheet_name = self.file.sheet_names[self.__current_idx]
        self.__current_idx += 1
        return sheet_name, self.get_sheet(sheet_name)

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

class XlsxHouseFileIterator:
    __current_idx = 1

    def __iter__(self):
        return self

    def __next__(self):
        if (self.__current_idx > 120):
            self.__current_idx = 1
            raise StopIteration
        house_name = "%03d" % self.__current_idx
        self.__current_idx += 1
        return house_name, Xlsx(f"./FactoryZero2019/{house_name}.xlsx")
