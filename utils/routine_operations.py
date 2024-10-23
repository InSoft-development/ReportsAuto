import re
import shutil
import errno

import pandas as pd

import yaml

from typing import Union, Tuple, List, Dict
from loguru import logger


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


def copy_recursively_objects_directory(src: str, dest: str) -> None:
    try:
        shutil.copytree(src, dest, dirs_exist_ok=True)
    except OSError as e:
        # Исключение если директория уже существует
        logger.warning(e)
        if e.errno != errno.EEXIST:
            logger.error(e)


def remove_recursively_objects_directory(path: str) -> None:
    shutil.rmtree(path)


def backup_recovery(config_path: str, config: dict, src_backup: str, dest_recovery: str) -> dict:
    # Восстанавливаем параметры конфига
    with open(config_path, 'w') as write_file:
        yaml.dump(config, write_file)

    with open(config_path, 'r') as read_file:
        config = yaml.safe_load(read_file)

    # Восстанавливаем директории с объектами
    remove_recursively_objects_directory(dest_recovery)
    copy_recursively_objects_directory(src_backup, dest_recovery)
    remove_recursively_objects_directory(src_backup)

    return config


def fill_plotly_interval_all(roll_df: pd.DataFrame, object_selected: str, group_selected: int,
                             json_interval: List[dict]) -> Tuple[List[dict], dict]:
    data = [{
        'x': roll_df.index.strftime("%Y-%m-%d %H:%M:%S").tolist(),
        'y': roll_df['target_value'].tolist(),
        'type': 'scatter'
    }]

    # Заполняем объект layout графика
    fill_shapes = lambda begin, end: {
        'type': 'rect',
        'xref': 'x',
        'yref': 'paper',
        'x0': begin,
        'y0': 0,
        'x1': end,
        'y1': 1,
        'line': {
            'width': 1,
            'color': 'red',
            'layer': 'below'
        }
    }
    layout = {
        'title': f'Объект: {object_selected}, Группа: {group_selected}',
        'autosize': True,
        'xaxis': {
            'type': 'date',
        },
        'shapes': [fill_shapes(interval['time'][0], interval['time'][1]) for interval in json_interval]
    }

    return data, layout


def fill_plotly_interval_specify(roll_df: pd.DataFrame, object_selected: str, group_selected: int,
                                 interval_num: int, json_interval: List[dict],
                                 params: Dict[str, int]) -> Tuple[List[dict], dict]:
    # Достаем начальные и конечные отсчеты времени и индексы интервалов
    begin, end = json_interval[interval_num]['time']
    begin_index, end_index = json_interval[interval_num]['index']

    # Обрабатываем отступы
    # TODO: параметры приходят из веба
    left_space = params['leftSpace']
    right_space = params['rightSpace']

    interval_len = end_index - begin_index
    if left_space < interval_len < begin_index:
        left_indentation = interval_len
    else:
        if begin_index > left_space:
            left_indentation = left_space
        else:
            left_indentation = 0
    if (interval_len > right_space) and (end_index < (len(roll_df) - right_space)) \
            and ((end_index + interval_len) < len(roll_df)):
        right_indentation = interval_len
    else:
        if end_index < (len(roll_df) - right_space):
            right_indentation = right_space
        else:
            right_indentation = 0

    # Заполняем данные графика
    begin_index -= left_indentation
    end_index += right_indentation

    data = [{
        'x': roll_df.iloc[begin_index:end_index].index.strftime("%Y-%m-%d %H:%M:%S").tolist(),
        'y': roll_df.iloc[begin_index:end_index]['target_value'].tolist(),
        'type': 'scatter',
    }]

    # Заполняем объект layout графика
    layout = {
        'title': f'Объект: {object_selected}, Группа: {group_selected}, Интервал: {begin} -- {end}',
        'autosize': True,
        'xaxis': {
            'type': 'date',
        },
        'shapes': [
            {
                'type': 'rect',
                'xref': 'x',
                'yref': 'paper',
                'x0': begin,
                'y0': 0,
                'x1': end,
                'y1': 1,
                'line': {
                    'width': 1,
                    'color': 'red',
                    'layer': 'below'
                }
            }
        ]
    }

    return data, layout

