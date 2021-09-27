import sys

def dump_csv(path, dict_array):
    with open(path, "w+") as file:
        stdout = sys.stdout
        sys.stdout = file

        print(','.join(dict_array[0].keys()))

        for it in dict_array:
            print(','.join(str(x) for x in it.values()))

        sys.stdout = stdout
