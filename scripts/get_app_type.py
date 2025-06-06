# This script parses the TOML file for the project and determines the type of web application
# Example output:
# fastapi
# click
# flask
# django
# streamlit
# reflex

import os
import tomllib
import subprocess

BASE = os.path.dirname(os.path.abspath(__file__))
MAIN = os.path.abspath(os.path.join(BASE, ".."))

python_binary = os.path.join(MAIN, ".python", "bin", "python")
app = subprocess.run([python_binary, os.path.join(BASE, "get_project_directory.py")], capture_output=True).stdout.decode("utf-8").strip()

if app.startswith("[WARN]"):
    print("[ERROR] - No application is configured in this repository.")
    exit(0)

def load_pyproject_toml(file_path: str = "pyproject.toml") -> dict:
    """Load and parse pyproject.toml file."""
    try:
        with open(file_path, "rb") as f:
            return tomllib.load(f)
    except FileNotFoundError:
        raise FileNotFoundError(f"pyproject.toml not found at {file_path}")
    except tomllib.TOMLDecodeError as e:
        raise ValueError(f"Invalid TOML syntax: {e}")

# This will print the name of the directory that contains the pyproject.toml file.
# NOTE: This assumes that there is only one such directory. - if there are multiple, it will print the first one it finds.
if os.path.exists(os.path.join(MAIN, app, "pyproject.toml")):
    # Let's scan the toml file for the packages - we want to know FastAPI, Click, etc.
    _toml_data = load_pyproject_toml(file_path=os.path.join(MAIN, app, "pyproject.toml"))


    if "fastapi" in _toml_data["tool"]["poetry"]["dependencies"].keys():
        print("fastapi")

    if "click" in _toml_data["tool"]["poetry"]["dependencies"].keys():
        print("click")

    if "flask" in _toml_data["tool"]["poetry"]["dependencies"].keys():
        print("flask")

    if "django" in _toml_data["tool"]["poetry"]["dependencies"].keys():
        print("django")

    if "streamlit" in _toml_data["tool"]["poetry"]["dependencies"].keys():
        print("streamlit")
    
    if "reflex" in _toml_data["tool"]["poetry"]["dependencies"].keys():
        print("reflex")
