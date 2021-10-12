from .FormatIterator import FormatIterator
from .Xlsx import Xlsx


class HouseXlsxIterator:
    def __init__(self, directory) -> None:
        self.__iterator = FormatIterator(range(1, 121), lambda it: "%s/%03d.xlsx" % (directory, it))

    def __iter__(self):
        return self

    def __next__(self):
        idx, path = self.__iterator.__next__()
        return "%03d" % idx, Xlsx(path)
