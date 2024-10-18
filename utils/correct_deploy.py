"""
Модуль содержит функции подготовки к развертыванию
"""
import os
import errno

import ipaddress
import shutil
import yaml

import pandas as pd

from loguru import logger

import utils.constants_and_paths as constants

from typing import Tuple


def application_structure() -> bool:
    """
    Процедура проверки структуры веб-приложения
    :return: True/False результат проверки структуры веб-приложения
    """
    logger.info(f"application_structure()")
    try:
        os.mkdir(f'{constants.OBJECTS}')
    except OSError as e:
        if e.errno != errno.EEXIST:
            logger.error(e)
            return False

    return True


def application_experiment_structure(object_path: str) -> None:
    """
    Процедура проверяет создание директорий для найденного объекта эксперимента
    :param object_path: путь к объекту эксперимента
    :return: None
    """
    logger.info(f"application_experiment_structure({object_path})")

    try:
        os.mkdir(f'{object_path}{constants.DATA_DIRECTORY}')
    except OSError as e:
        if e.errno != errno.EEXIST:
            logger.error(e)

    try:
        os.mkdir(f'{object_path}{constants.DATA_CSV_ROLLED}')
    except OSError as e:
        if e.errno != errno.EEXIST:
            logger.error(e)

    try:
        os.mkdir(f'{object_path}{constants.DATA_JSON_INTERVAL}')
    except OSError as e:
        if e.errno != errno.EEXIST:
            logger.error(e)

    try:
        os.mkdir(f'{object_path}{constants.REPORTS_DIRECTORY}')
    except OSError as e:
        if e.errno != errno.EEXIST:
            logger.error(e)


def application_deploy(path: str) -> dict:
    """
    Процедура разворачивания веб-приложения
    :param path: путь к директории эксперимента
    :return: None
    """
    logger.info(f"application_deploy({path})")
    # Инициализация словаря путей
    config_path = {}

    # Чтение конфига станций config_station.yaml с использование пути от тестсьюта
    testsuite_path, experiment_date = path.split('Archive')

    with open(testsuite_path+constants.CONFIG_STATION, 'r') as read_file:
        config_station = yaml.safe_load(read_file)

    with open(testsuite_path+constants.CONFIG_EXP, 'r') as read_file:
        config_exp = yaml.safe_load(read_file)

    # Создание директорий под объекты экспериментов
    for station_name, station_data in config_station['Station'].items():
        try:
            os.mkdir(f"{constants.OBJECTS}{station_name.lower()}")
        except OSError as e:
            if e.errno != errno.EEXIST:
                logger.error(e)

        # Создание директорий файлов для объекта эксперимента
        application_experiment_structure(constants.OBJECTS+station_name.lower()+os.sep)

        # Создание словаря путей
        config_path = application_create_path_dict(config_path, station_name.lower(), station_data, testsuite_path, path)

    # Создание мини-конфига объекта
    config = application_create_config(config_station['Station'], config_exp, testsuite_path)
    # Сохранение мини-конфига объекта
    with open(constants.CONFIG, 'w') as write_file:
        yaml.dump(config, write_file)

    return config_path


def application_create_config(config_station: dict, config_experiment: dict, testsuite_path: str) -> dict:
    """
    Функция создания мини-конфига
    :param config_station: конфиг станций
    :param config_experiment: конфиг эксперимента тестсьюта
    :param testsuite_path: асболютный путь до тестсьюта
    :return: Dict мини-конфиг
    """
    logger.info(f"application_create_config(config_station, config_experiment)")
    config = {}
    for station_name, station_data in config_station.items():
        config[station_name.lower()] = {
            'data': os.path.join(testsuite_path, station_data['data']),
            'power_index': station_data['power_index'],
            'power_limit': station_data['power_limit'],
            'number_of_sample': station_data['number_of_sample'],
            'count_of_groups': validate_count_of_groups(os.path.join(testsuite_path, station_data['kks']))
        }

    config['post_processing'] = {
        'roll_in_hours': config_experiment['roll_in_hours'],
        'threshold_short': config_experiment['threshold_short'],
        'threshold_long': config_experiment['threshold_long'],
        'len_long': config_experiment['len_long'],
        'len_short': config_experiment['len_short'],
        'count_continue_short': config_experiment['count_continue_short'],
        'count_continue_long': config_experiment['count_continue_long'],
        'count_top': config_experiment['count_top']
    }

    return config


def application_create_path_dict(config: dict, name: str, data: dict, testsuite_path, archive_path) -> dict:
    """
    Функция создания словаря путей файлов и директорий
    :param config: словарь путей
    :param name: наименование объекта из конфига станций
    :param data: данные по объекту из конфига станций
    :param testsuite_path: абсолютный путь до тестсьюта
    :param archive_path: абсолютный путь до эксперимента
    :return:
    """
    logger.info(f"application_create_path_dict(config, name, data, testsuite_path, archive_path)")
    config[name] = {
        'slices': os.path.join(testsuite_path, data['data']),
        'kks_with_groups': os.path.join(testsuite_path, data['kks']),
        'predict': os.path.join(archive_path, name, 'csv_predict'),
        'loss': os.path.join(archive_path, name, 'csv_loss'),
        'roll': os.path.join(constants.OBJECTS, name, constants.DATA_CSV_ROLLED),
        'json_interval': os.path.join(constants.OBJECTS, name, constants.DATA_JSON_INTERVAL),
        'reports': os.path.join(constants.OBJECTS, name, constants.REPORTS_DIRECTORY)
    }

    return config


def validate_count_of_groups(kks_with_groups_object_path: str) -> int:
    """
    Функция возвращает количество групп для объекта
    :param kks_with_groups_object_path: путь до файла kks и групп
    :return:
    """
    logger.info(f"validate_count_of_groups({kks_with_groups_object_path})")
    kks_with_groups = pd.read_csv(kks_with_groups_object_path, usecols=['group'], sep=';')
    logger.info(set(kks_with_groups['group']))
    return len(set(kks_with_groups['group']))


def validate_dir_path(path: str) -> bool:
    """
    Функция проверки существования пути
    :param path: путь к директории эксперимента
    :return: True/False результат проверки существования пути
    """
    logger.info(f"validate_dir_path({path})")
    return os.path.isdir(path)


def validate_ip_and_port(ip: str, port: int) -> bool:
    """
    Функция валидации IPv4 адреса
    :param ip: строка IP-адреса
    :param port: порт
    :return: True/False результат валидации строки в IPv4 адрес
    """
    logger.info(f"validate_ip_and_port({ip}, {port})")
    try:
        ipaddress.ip_address(ip)
        if 1 <= port <= 65535:
            return True
        return False
    except ValueError as ip_validate_error:
        logger.error(ip_validate_error)
        return False
