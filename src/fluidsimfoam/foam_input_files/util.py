"""Utilities"""
from typing import Union


def as_dict(data: Union[dict, str], filter_comments=True) -> dict:
    """return a dict, potentially by converting a str"""
    if isinstance(data, dict):
        return data
    elif isinstance(data, str):
        data_as_str = data
        data = {}
        for line in data_as_str.strip().split("\n"):
            line = line.strip().removesuffix(";")
            if any(line.startswith(comment_char) for comment_char in ("//", "#")):
                if filter_comments:
                    continue
                else:
                    key, value = line, None
            else:
                key, value = line.split(maxsplit=1)
            data[key] = value
        return data
    else:
        raise TypeError
