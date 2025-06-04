# This script is going to find and print out the name of the folder that contains the pyproject.toml file.
import os

BASE = os.path.dirname(os.path.abspath(__file__))
MAIN = os.path.abspath(os.path.join(BASE, ".."))
           
dir_list = [i for i in os.listdir(MAIN) if os.path.isdir(os.path.join(MAIN, i)) and not i.startswith(".") and i != "scripts"]

if not dir_list:
    print("[WARN] - No project directory found.")
    exit(0)

# This will print the name of the directory that contains the pyproject.toml file.
# NOTE: This assumes that there is only one such directory. - if there are multiple, it will print the first one it finds.
for i in dir_list:
    if os.path.exists(os.path.join(MAIN, i, "pyproject.toml")):
        print(i)
        exit(0)
