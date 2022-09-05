from coronainfo.enums import Paths


def cache_file(file_name: str, content: str):
    """Caches the specified file at the app's cache directory, which is at `~/.cache/corona-info/`

    Parameters
    ----------
    file_name : str
        A string of the file's name.
    content : str
        A string of the content that will be written into the specified file.
    """
    path = Paths.CACHE_DIR / file_name
    with open(path, "w") as file:
        file.write(content)


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
