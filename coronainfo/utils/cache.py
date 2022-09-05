import os
from pathlib import Path


def get_cache_dir(file_name: str = None) -> str:
    """Gets the cache directory of `corona-info`.

    The cache directory is located in `~/.cache/corona-info`. This function will automatically create 
    the directories if necessary. If given a file name, it will directly return the path to the file 
    instead.
    
    Parameters
    ----------
    file_name: str, optional
        A string of the file's name.

    Returns
    -------
    str
        A string of the path of the cache directory.
    """

    cache_dir = Path(Path.home(), ".cache", "corona-info")
    if not cache_dir.exists():
        cache_dir.mkdir(parents=True, exist_ok=True)

    if file_name is not None:
        cache_dir = cache_dir / file_name

    return str(cache_dir)


def cache_file(file_name: str, content: str):
    """Caches the specified file at the app's cache directory, which is at `~/.cache/corona-info/`

    Parameters
    ----------
    file_name : str
        A string of the file's name.
    content : str
        A string of the content that will be written into the specified file.
    """
    path = os.path.join(get_cache_dir(), file_name)
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
