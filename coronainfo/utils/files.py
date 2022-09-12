import json
from typing import Union
from pathlib import Path


def write_file(file_path: Union[str, Path], content: str):
    with open(file_path, "w") as file:
        file.write(content)


def write_json(file_path: Union[str, Path], json_data):
    with open(file_path, "w") as file:
        json.dump(json_data, file)


def get_json(file_path: Union[str, Path]):
    with open(file_path, "r") as file:
        return json.load(file)


def get_file_content(file_path: str) -> str:
    """
    Gets the contents of the file at the given file path.

    Parameters
    ----------
    file_path: str
        A string of the path of the file.

    Returns
    -------
    str
        A string of the given file's contents.
    """
    with open(file_path, "r") as file:
        return file.read()
