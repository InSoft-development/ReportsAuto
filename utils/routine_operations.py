import re
import os
import shutil
import errno

import pandas as pd
import numpy as np
from scipy.stats import rv_histogram

import yaml

from typing import Union, Tuple, List, Dict
from loguru import logger


def to_camel_case(snake_str: str) -> str:
    """
    Функция перевода из snake_case в camelCase
    :param snake_str: строка в snake_case
    :return: строка в camelCase
    """
    return "".join(x.capitalize() for x in snake_str.lower().split("_"))


def to_lower_camel_case(snake_str: str) -> str:
    """
    Функция перевода из snake_case в camelCase кроме первого символа
    :param snake_str: строка в snake_case
    :return: строка в camelCase
    """
    camel_string = to_camel_case(snake_str)
    return snake_str[0].lower() + camel_string[1:]


def to_snake_case(camel_str: str) -> str:
    """
    Функция перевода из camelCase в snake_case
    :param camel_str: строка в camelCase
    :return: строка в snake_case
    """
    pattern = re.compile(r'(?<!^)(?=[A-Z])')
    return pattern.sub('_', camel_str).lower()


def dict_to_lower_camel_case(snake_dict: Dict[str, int]) -> Dict[str, int]:
    """
    Функция перевода ключей словаря из snake_case в camelCase
    :param snake_dict: словарь, ключи которого в snake_case
    :return: словарь с ключами в camelCase
    """
    camel_dict = {}
    for key in snake_dict:
        camel_dict[to_lower_camel_case(key)] = snake_dict[key]
    return camel_dict


def dict_to_snake_case(camel_dict: Dict[str, int]) -> Dict[str, int]:
    """
    Функция перевода ключей словаря из camelCase в snake_case
    :param camel_dict: словарь, ключи которого в camelCase
    :return: словарь с ключами в snake_case
    """
    snake_dict = {}
    for key in camel_dict:
        snake_dict[to_snake_case(key)] = camel_dict[key]
    return snake_dict


def copy_recursively_objects_directory(src: str, dest: str) -> None:
    """
    Процедура рекурсивного копирования директорий объектов
    :param src: путь директории объектов
    :param dest: путь директории для бэкапа
    :return: None
    """
    try:
        shutil.copytree(src, dest, dirs_exist_ok=True)
    except OSError as e:
        # Исключение если директория уже существует
        logger.warning(e)
        if e.errno != errno.EEXIST:
            logger.error(e)


def remove_recursively_objects_directory(path: str) -> None:
    """
    Процедура рекурсивного удаления директории
    :param path: путь директории, подлежащей удалению
    :return: None
    """
    shutil.rmtree(path)


def backup_recovery(config_path: str, config: dict, src_backup: str, dest_recovery: str) -> dict:
    """
    Функция восстановления бэкапа исходного конфига и объекта
    :param config_path: путь до конфига
    :param config: объект конфига, который будет восстановлен
    :param src_backup: путь до диретории бэкапа
    :param dest_recovery: путь до директории, в которой нужно восстановить директории объектов
    :return: восстановленный конфиг
    """
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


def remove_reports(objects_dir: str) -> None:
    """
    Процедура удаления директорий отчетов объектов
    :param objects_dir: путь директории с объектами
    :return: None
    """
    for object_directory in os.listdir(objects_dir):
        report_directory_path = os.path.join(objects_dir, object_directory, 'reports')
        logger.warning(f"removing {report_directory_path}")
        remove_recursively_objects_directory(report_directory_path)
        os.mkdir(report_directory_path)
        logger.success(f"removed {report_directory_path}")


def define_additional_signals(kks_with_groups: pd.DataFrame,
                              main_signal_kks: str, power_kks: str,
                              palette_power: str, palette_other: List[str]) -> List[Dict[str, str]]:
    """
    Функция определения объектов дополнительных сигналов: kks, описание, цвет
    :param kks_with_groups: фрейм kks, групп и описания датчиков
    :param main_signal_kks: kks основного датчика в многоосевом графике
    :param power_kks: kks датчика мощности из конфига
    :param palette_power: фиксированный цвет датчика мощности
    :param palette_other: фиксированная палетта для остальных датчиков группы
    :return: массив объектов дополнительных сигналов: kks, описание, цвет
    """
    clause = (kks_with_groups['group'] == 0) & (kks_with_groups['kks'] != main_signal_kks) & \
             (kks_with_groups['kks'] != power_kks)
    clause_for_power_descr = kks_with_groups['kks'] == power_kks

    additional_signals = kks_with_groups.loc[clause]['kks'].tolist()[:3]
    additional_signals_descr = kks_with_groups.loc[clause]['name'].tolist()[:3]

    # Определяем палетту для применения цвета к чекбоксу для дополнительных сигналов
    palette = palette_other[:len(additional_signals)]

    # Добавляем в начала списков сигнал мощности, его описание и цвет, если он не главный сигнал
    if main_signal_kks != power_kks:
        additional_signals.insert(0, power_kks)
        additional_signals_descr.insert(0, kks_with_groups.loc[clause_for_power_descr]['name'].values[0])
        palette.insert(0, palette_power)

    return [{'kks': kks, 'description': descr, 'color': color} for kks, descr, color in
            zip(additional_signals, additional_signals_descr, palette)]


def define_signals(kks_with_groups: pd.DataFrame, main_signal_kks: str, power_kks: str,
                   palette_main: str, palette_power: str, palette_other: List[str],
                   active_signals: List[str] = None) -> List[Dict[str, str]]:
    """
    Функция определения объектов сигналов: kks, описание, цвет
    :param kks_with_groups: фрейм kks, групп и описания датчиков
    :param main_signal_kks: kks основного датчика в многоосевом графике
    :param power_kks: kks датчика мощности из конфига
    :param palette_main: фиксированный цвет датчика основного сигнала многоосевого графика
    :param palette_power: фиксированный цвет датчика мощности
    :param palette_other: фиксированная палетта для остальных датчиков группы
    :param active_signals: список активных сигналов многоосевого графика
    :return: массив объектов дополнительных сигналов: kks, описание, цвет
    """
    clause = (kks_with_groups['group'] == 0) & (kks_with_groups['kks'] != main_signal_kks) & \
             (kks_with_groups['kks'] != power_kks)
    clause_for_power_descr = kks_with_groups['kks'] == power_kks
    clause_for_main = kks_with_groups['kks'] == main_signal_kks

    signals = kks_with_groups.loc[clause]['kks'].tolist()[:3]
    signals_descr = kks_with_groups.loc[clause]['name'].tolist()[:3]

    # Определяем палетту для применения цвета к чекбоксу для дополнительных сигналов
    palette = palette_other[:len(signals)]

    # Добавляем в начала списков сигнал мощности, его описание и цвет, если он не главный сигнал
    if main_signal_kks != power_kks:
        signals.insert(0, power_kks)
        signals_descr.insert(0, kks_with_groups.loc[clause_for_power_descr]['name'].values[0])
        palette.insert(0, palette_power)

    signals.insert(0, main_signal_kks)
    signals_descr.insert(0, kks_with_groups.loc[clause_for_main]['name'].values[0])
    palette.insert(0, palette_main)
    logger.info(signals)

    defined_signals = [{'kks': kks, 'description': descr, 'color': color} for kks, descr, color in
                       zip(signals, signals_descr, palette)]

    if active_signals is not None:
        defined_signals = [signal for signal in defined_signals if signal['kks'] in active_signals]

    return defined_signals


def fill_plotly_interval_all(roll_df: pd.DataFrame, object_selected: str, group_selected: int,
                             json_interval: List[dict]) -> Tuple[List[dict], dict]:
    """
    Функция заполнения data и layout графика вероятности на всем фрейме
    :param roll_df: фрейм сглаженных данных вероятности (предикта)
    :param object_selected: выбранный объект
    :param group_selected: выбранная группа
    :param json_interval: json с выделенными интервалами
    :return: data и layout графика вероятности на всем фрейме
    """
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
                                 interval_num: int, json_interval: List[dict]) -> Tuple[List[dict], dict]:
    """
    Функция заполнения data и layout графика вероятности на интервале
    :param roll_df: фрейм сглаженных данных вероятности (предикта)
    :param object_selected: выбранный объект
    :param group_selected: выбранная группа
    :param interval_num: номер выбранного интервала
    :param json_interval: json с выделенными интервалами
    :return: data и layout графика вероятности на интервале
    """
    # Достаем начальные и конечные отсчеты времени и индексы интервалов
    begin, end = json_interval[interval_num]['time']
    begin_index, end_index = json_interval[interval_num]['index']

    interval_len = end_index - begin_index
    if begin_index < interval_len:
        begin_index = 0
    else:
        begin_index -= interval_len
    if end_index + interval_len > len(roll_df):
        end_index = len(roll_df)
    else:
        end_index += interval_len

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


def fill_plotly_multi_axes(slice_df: pd.DataFrame, interval_num: int, signals: List[str],
                           active_signals: List[str], json_interval: List[dict],
                           params: Dict[str, Union[int, str, dict]]) -> Tuple[List[dict], dict]:
    """
    Функция заполнения data и layout многоосевого графика
    :param slice_df: фрейм исходных данных срезов
    :param interval_num: номер выбранного интервала
    :param signals: список сигналов
    :param active_signals: список активных сигналов
    :param json_interval: json с выделенными интервалами
    :param params: словарь с параметрами
    :return: data и layout многоосевого графика
    """
    # Достаем начальные и конечные отсчеты времени и индексы интервалов
    begin, end = json_interval[interval_num]['time']
    begin_index, end_index = json_interval[interval_num]['index']

    interval_len = end_index - begin_index
    if begin_index < interval_len:
        begin_index = 0
    else:
        begin_index -= interval_len
    if end_index + interval_len > len(slice_df):
        end_index = len(slice_df)
    else:
        end_index += interval_len

    # Заполняем объект layout графика
    fill_data = lambda order, kks: {
        'x': slice_df.iloc[begin_index:end_index].index.strftime("%Y-%m-%d %H:%M:%S").tolist(),
        'y': slice_df.iloc[begin_index:end_index][kks].tolist(),
        'name': kks,
        'yaxis': f'y{order}',
        'type': 'scatter',
    }
    data = [fill_data(index+1, signal) for index, signal in enumerate(active_signals)]

    layout = {
        'title': params['main_signal'],
        'autosize': True,
        'xaxis': {
            'type': 'date'
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
        ],
        'showlegend': False
    }

    active_index = 0
    other_index = 0
    if (params['main_signal'] not in active_signals) and (params['power'] in active_signals):
        for index, signal in enumerate(signals):
            if signal in active_signals:
                if signal == params['power']:
                    data[active_index]['line'] = {
                        'color': params['palette']['power'],
                        'width': 1
                    }
                    layout[f'yaxis'] = {
                        'title': {
                            'text': signal,
                            'font': {
                                'color': params['palette']['power'],
                                'size': 14
                            }
                        },
                        'tickfont': {
                            'color': params['palette']['power'],
                            'size': 14
                        },
                        'autoshift': True,
                        'anchor': 'free',
                        'layer': 'below traces',
                        'overlaying': 'y2',
                        'showgrid': False,
                        'showline': True,
                        'side': 'right',
                        'ticks': 'outside',
                        'tickcolor': 'black',
                        'title_standoff': 10,
                        'tickwidth': 0.5,
                        'zeroline': False,
                    }
                else:
                    if active_index == 1:
                        data[active_index]['line'] = {
                            'color': params['palette']['other'][other_index],
                            'width': 1
                        }
                        layout[f'yaxis{active_index+1}'] = {
                            'title': {
                                'text': signal,
                                'font': {
                                    'color': params['palette']['other'][other_index],
                                    'size': 14
                                }
                            },
                            'tickfont': {
                                'color': params['palette']['other'][other_index],
                                'size': 14
                            }
                        }
                    else:
                        data[active_index]['line'] = {
                            'color': params['palette']['other'][other_index],
                            'width': 1
                        }
                        layout[f'yaxis{active_index+1}'] = {
                            'title': {
                                'text': signal,
                                'font': {
                                    'color': params['palette']['other'][other_index],
                                    'size': 14
                                }
                            },
                            'tickfont': {
                                'color': params['palette']['other'][other_index],
                                'size': 14
                            },
                            'autoshift': True,
                            'anchor': 'free',
                            'layer': 'below traces',
                            'overlaying': 'y2',
                            'showgrid': False,
                            'showline': True,
                            'side': 'left',
                            'ticks': 'outside',
                            'tickcolor': 'black',
                            'tickwidth': 0.5,
                            'zeroline': False
                        }
                    other_index += 1
                active_index += 1
            if (signal not in active_signals) and (signal != params['main_signal']) and (signal != params['power']):
                other_index += 1
    else:
        for index, signal in enumerate(signals):
            if signal in active_signals:
                if signal == params['main_signal']:
                    data[active_index]['line'] = {
                        'color': params['palette']['main'],
                        'width': 1
                    }
                    layout[f'yaxis{active_index + 1}'] = {
                        'title': {
                            'text': signal,
                            'font': {
                                'color': params['palette']['main'],
                                'size': 14
                            }
                        },
                        'tickfont': {
                            'color': params['palette']['main'],
                            'size': 14
                        }
                    }
                elif signal == params['power']:
                    data[active_index]['line'] = {
                        'color': params['palette']['power'],
                        'width': 1
                    }
                    layout[f'yaxis{active_index + 1}'] = {
                        'title': {
                            'text': signal,
                            'font': {
                                'color': params['palette']['power'],
                                'size': 14
                            }
                        },
                        'tickfont': {
                            'color': params['palette']['power'],
                            'size': 14
                        },
                        'autoshift': True,
                        'anchor': 'free',
                        'layer': 'below traces',
                        'overlaying': 'y',
                        'showgrid': False,
                        'showline': True,
                        'side': 'right',
                        'ticks': 'outside',
                        'tickcolor': 'black',
                        'title_standoff': 10,
                        'tickwidth': 0.5,
                        'zeroline': False,
                    }
                else:
                    if active_index == 0:
                        data[active_index]['line'] = {
                            'color': params['palette']['other'][other_index],
                            'width': 1
                        }
                        layout[f'yaxis{active_index + 1}'] = {
                            'title': {
                                'text': signal,
                                'font': {
                                    'color': params['palette']['other'][other_index],
                                    'size': 14
                                }
                            },
                            'tickfont': {
                                'color': params['palette']['other'][other_index],
                                'size': 14
                            }
                        }
                    else:
                        data[active_index]['line'] = {
                            'color': params['palette']['other'][other_index],
                            'width': 1
                        }
                        layout[f'yaxis{active_index + 1}'] = {
                            'title': {
                                'text': signal,
                                'font': {
                                    'color': params['palette']['other'][other_index],
                                    'size': 14
                                }
                            },
                            'tickfont': {
                                'color': params['palette']['other'][other_index],
                                'size': 14
                            },
                            'autoshift': True,
                            'anchor': 'free',
                            'layer': 'below traces',
                            'overlaying': 'y',
                            'showgrid': False,
                            'showline': True,
                            'side': 'left',
                            'ticks': 'outside',
                            'tickcolor': 'black',
                            'tickwidth': 0.5,
                            'zeroline': False
                        }
                    other_index += 1
                active_index += 1
            if (signal not in active_signals) and (signal != params['main_signal']) and (signal != params['power']):
                other_index += 1

    return data, layout


def fill_plotly_histogram(loss: pd.DataFrame, threshold_short: int, threshold_long: int) -> Tuple[List[dict], dict]:
    """
    Функция заполнения data и layout гистограммы
    :param loss: фрейм лосса
    :param threshold_short: порог по вероятности выделения коротких интервалов
    :param threshold_long: порог по вероятности выделения длинных интервалов
    :return: data и layout гистограммы
    """
    # Вычисляем средний loss по датчикам в каждом отсчете времени, предварительно заполнив Nan нулями
    loss_mean = loss.fillna(0).mean(axis=1, skipna=True).values.tolist()

    # Гистограмма количества вхождений значения loss в интервал
    hist = np.histogram(loss_mean, bins=100)
    # Распределение, заданное гистограммой
    dist = rv_histogram(hist)
    # Разбиение на интервалы от минимального до максимального значения
    partition = np.arange(min(loss_mean), max(loss_mean), 0.01).tolist()
    dist_cdf_list = list(100 * dist.cdf(partition))

    # Ближайшие значения вероятности порогов на функции распределения
    short_abs = min([abs(f - threshold_short) for f in dist_cdf_list])
    x_short = [f for f in dist_cdf_list if abs(f - threshold_short) == short_abs][0]

    long_abs = min([abs(f - threshold_long) for f in dist_cdf_list])
    x_long = [f for f in dist_cdf_list if abs(f - threshold_long) == long_abs][0]

    data = [
        {
            'x': partition,
            'y': list(100 * dist.pdf(partition)),
            'type': 'scatter',
            'name': 'loss (PDF)',
        },
        {
            'x': partition,
            'y': list(100 * dist.cdf(partition)),
            'type': 'scatter',
            'name': 'Вероятность (CDF)',
        }
    ]

    layout = {
        'title': f'Порог коротких интервалов: {threshold_short}, Порог длинных интервалов: {threshold_long}',
        'shapes': [
            {
                'type': 'line',
                'xref': 'x',
                'yref': 'paper',
                'x0': partition[dist_cdf_list.index(x_short)],
                'y0': 0,
                'x1': partition[dist_cdf_list.index(x_short)],
                'y1': 1,
                'line': {
                    'width': 1,
                    'color': '#2ca02c',
                    'layer': 'below'
                }
            },
            {
                'type': 'line',
                'xref': 'x',
                'yref': 'paper',
                'x0': partition[dist_cdf_list.index(x_long)],
                'y0': 0,
                'x1': partition[dist_cdf_list.index(x_long)],
                'y1': 1,
                'line': {
                    'width': 1,
                    'color': '#9467bd',
                    'layer': 'below'
                }
            }
        ],
        'annotations': [
            {
                'showarrow': False,
                'text': 'threshold_short',
                'font': {
                    'color': '#2ca02c',
                    'size': 8
                },
                'x': partition[dist_cdf_list.index(x_short)],
                'xref': 'x',
                'xanchor': 'left' if partition[dist_cdf_list.index(x_short)] > partition[dist_cdf_list.index(x_long)]
                else 'right',
                'y': 0,
                'yref': 'paper'
            },
            {
                'showarrow': False,
                'text': 'threshold_long',
                'font': {
                    'color': '#9467bd',
                    'size': 8
                },
                'x': partition[dist_cdf_list.index(x_long)],
                'xref': 'x',
                'xanchor': 'right' if partition[dist_cdf_list.index(x_short)] > partition[dist_cdf_list.index(x_long)]
                else 'left',
                'y': 0,
                'yref': 'paper'
            }
        ],
        'showlegend': False,
        'xaxis': {
            'title': 'Распределение loss'
        },
        'yaxis': {
            'title': 'Количество попаданий'
        }
    }

    return data, layout
