import re

from typing import Union, Tuple, List, Dict


def to_camel_case(snake_str: str) -> str:
    return "".join(x.capitalize() for x in snake_str.lower().split("_"))


def to_lower_camel_case(snake_str: str) -> str:
    # We capitalize the first letter of each component except the first one
    # with the 'capitalize' method and join them together.
    camel_string = to_camel_case(snake_str)
    return snake_str[0].lower() + camel_string[1:]


def to_snake_case(camel_str: str) -> str:
    pattern = re.compile(r'(?<!^)(?=[A-Z])')
    return pattern.sub('_', camel_str).lower()


def dict_to_lower_camel_case(snake_dict: Dict[str, int]) -> Dict[str, int]:
    camel_dict = {}
    for key in snake_dict:
        camel_dict[to_lower_camel_case(key)] = snake_dict[key]
    return camel_dict


def dict_to_snake_case(camel_dict: Dict[str, int]) -> Dict[str, int]:
    snake_dict = {}
    for key in camel_dict:
        snake_dict[to_snake_case(key)] = camel_dict[key]
    return snake_dict

