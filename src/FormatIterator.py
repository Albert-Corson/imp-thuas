class FormatIterator:
    __current_idx = 1

    def __init__(self, enumerator, key) -> None:
        self.__enumerator = enumerator
        self.__key = key
        r = range(1, 20)

    def __iter__(self):
        return self

    def __next__(self):
        if (self.__current_idx >= len(self.__enumerator)):
            self.__current_idx = 0
            raise StopIteration

        cur = self.__key(self.__enumerator[self.__current_idx])
        self.__current_idx += 1
        return self.__current_idx - 1, str(cur)
