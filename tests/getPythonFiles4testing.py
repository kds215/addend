# name getPythonFiles4testing.py

import shutil

list_of_files = "./source/pytestfiles.txt"
destination_folder = "./orig2/"

with open(list_of_files, "r") as source:
    for line in source:
        fullpath_name = line[:-1]
        shutil.copy(fullpath_name, destination_folder)
        print(f"copied: {fullpath_name}")
