import re
import types
import typing


def is_float(text: str) -> bool:
    """
    Checks if the given string is a float.

    Parameters
    ----------
    text : str
        A string which may contain a float/decimal number.

    Returns
    -------
    bool
        A boolean of whether the given string is a float number or not.
    """
    match = re.match(r"^\d*\.\d*$", text.strip())

    return bool(match)


def convert_to_num(text: str) -> typing.Union[int, float, str]:
    """
    Converts a string into either an int or float, depending on the string given. Returns the original string if it
    is not a number.

    Parameters
    ----------
    text: str
        A string that may or may not be converted into int or float.

    Returns
    -------
    int | float | str
        An int or float if the given string is a number. A string of the original string.

    """
    result = text

    if not result:
        result = 0

    # For values that have a + or - at the start
    elif len(result) > 0:
        temp = result[0:]
        if len(temp) > 0 and (temp[0] == "+" or temp[0] == "-"):
            temp = temp[1:]

        if temp.isdigit():
            result = int(result)
        elif is_float(temp):
            result = float(result)

    return result


def spread_subtypes(subtypes: tuple, accumulator: tuple = ()) -> tuple:
    """
    A recursive function that 'spreads' out subtype hints. For example, [int | None, str] returns [int, None,
    str]. This method does not consider nested type hints, like list[list[int]].

    Parameters
    ----------
    subtypes: tuple
        A tuple of typehints
    accumulator: set
        A set of typehints
    Returns
    -------
    list
        A tuple of subtypes
    """
    for subtype in subtypes:
        if not isinstance(subtype, types.UnionType):
            accumulator += (subtype,)
            continue

        accumulator += spread_subtypes(typing.get_args(subtype))

    result = set(accumulator)  # Remove duplications
    return tuple(result)
