import json, os
from addons.errors import InvalidArgError
from pathlib import Path
from typing import Union

def data_from_file(path: Path) -> Union[dict[str, str], list[str]]:
    """ opens a json or txt file and loads the data from it

    :param path: the path to the file being opened
    :returns: the data loaded from the file
    :rtype: dict or str list
    """
    if not isinstance(path, Path):
        path = Path(path)

    if not path.is_file() and path.exists():
        raise InvalidArgError(path, data_from_file)

    if not path.exists(): return None
    
    if path.suffix == '.json':
        with path.open() as f:
            data = json.load(f)
            return data
    
    elif path.suffix == '.lang' or path.suffix == '.txt':
        with path.open() as f:
            data = f.readlines()
            return data

    else:
        return None

def write_to_file(path: Path, data: Union[dict[str, str], list[str]], writing: bool = True):
    """ Writes a python dictionary to a JSON file

    :param path: the path and file name where the file should be written
    :param data: a python dictionary or list of striings to convert to json format or to loop through and add to a text file
    :type data: dict or list of strings
    :param writing: a boolean as to whether or not the file being written to is being written new or edited
    """
    if not isinstance(path, Path):
        path = Path(path)

    valid_files = ['.json', '.lang', '.txt']
    if path.suffix not in valid_files:
        raise InvalidArgError(path, write_to_file)

    if path.suffix == '.json':
        if writing:
            with path.open('w') as f:
                json.dump(data, f, indent = 4, sort_keys=True)

        else:
            with path.open('r+') as f:
                f.seek(0)
                json.dump(data, f, indent=4, sort_keys=True)
                f.truncate()

    else:
        if writing:
            with path.open('w') as f:
                for line in data:
                    f.write(line+"\n")

        else:
            with path.open('a') as f:
                for line in data:
                    f.write(line+"\n")