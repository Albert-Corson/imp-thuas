import os
import sys


class CSVDumper:
    @staticmethod
    def dump_array_of_dict(arr_of_dict, path=None, sep=','):
        if path != None:
            os.makedirs(os.path.dirname(path), exist_ok=True)
        with (sys.stdout if path == None else open(path, "w+")) as file:
            print(sep.join(arr_of_dict[0].keys()), file=file)
            for it in arr_of_dict:
                print(sep.join(str(x) for x in it.values()), file=file)

    @staticmethod
    def dump_dict_in_files(dictionary, directory=None, sep=','):
        if directory != None:
            os.makedirs(directory, exist_ok=True)
        for key in dictionary.keys():
            CSVDumper.dump_array_of_dict(
                dictionary[key], None if directory == None else f"{directory}/{key}.csv")

    @staticmethod
    def dump_dict(dictionary, columns_name, path=None, sep=','):
        if path != None:
            os.makedirs(os.path.dirname(path), exist_ok=True)
        with (sys.stdout if path == None else open(path, "w+")) as file:
            print(sep.join(columns_name), file=file)
            for key, value in dictionary.items():
                print("%s,%s" % (str(key), str(value)))
