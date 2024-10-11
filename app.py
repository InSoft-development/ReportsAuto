from flask import Flask
from flask_cors import CORS
from flask.helpers import send_file

import os
import argparse
import time
import shutil
import json
import yaml

from bs4 import BeautifulSoup as bs
import pandas as pd
from loguru import logger

import datetime
from dateutil.parser import parse

import subprocess
import signal

import utils.constants_and_paths as constants
import utils.correct_deploy as deploy

VERSION = '1.0.0'

clients = {}
config_path = None
config = None

app = Flask(__name__, static_folder="./web", template_folder="./web", static_url_path="")
CORS(app)


@app.route('/')
def hello():
    """
    Функция для проверки работы веб-сервера Flask
    :return: Возвращает заголовок при запросе URL на порт Flask
    """
    return "<h1> HELLO WORLD </h1>"


def parse_args():
    parser = argparse.ArgumentParser(description="start flask + vue 3 ReportAuto web-application")
    parser.add_argument("-p", "--path", type=str, help="specify path of experiment", required=True)
    parser.add_argument("-ip", "--host", type=str, help="specify IPv4 address of host", required=True)
    parser.add_argument("-po", "--port", type=int, help="specify port", required=True)
    parser.add_argument("-v", "--version", action="version", help="print version", version=f'{VERSION}')
    return parser.parse_args()


if __name__ == '__main__':
    try:
        args = parse_args()
    except SystemExit:
        logger.info(f'{VERSION} flask + vue 3 ReportAuto web-application version')
        exit(0)

    # Проверка введенных аргументов командной строки
    # Валидация IPv4-адреса и порта
    if not deploy.validate_ip_and_port(args.host, args.port):
        exit(0)

    # Валидация существования пути
    if not deploy.validate_dir_path(args.path):
        logger.error(f"{args.path} not exist!")
        exit(0)

    # Деплой структуры веб-приложения
    if not deploy.application_structure():
        logger.error(f"Check sources of web-app!")
        exit(0)

    # Получение словаря путей всех файлов и сохранение мини-конфига эксперимента
    config_path = deploy.application_deploy(args.path)

    # Чтение мини-конфига эксперимента
    with open(constants.CONFIG, 'r') as read_file:
        config = yaml.safe_load(read_file)

    logger.info(config_path)
    logger.info(config)

    # Запуск первоначального выделения интервалов
    arguments = ["python", "./get_interval.py", "-s", args.path, "-d", os.getcwd(),
                 "-c", os.path.join(os.getcwd(), constants.CONFIG)]
    logger.info(' '.join(arguments))
    try:
        p_get_interval = subprocess.Popen(arguments, stdout=subprocess.PIPE,
                                          cwd=os.path.join(os.getcwd(), 'utils'))
        p_get_interval.wait()
        # out_p_get_interval, err_p_get_interval = p_get_interval.communicate()
        # subprocess.run(arguments, capture_output=True, cwd=os.path.join(os.getcwd(), 'utils'), check=True)
    except subprocess.CalledProcessError as subprocess_exception:
        logger.error(subprocess_exception)
        exit(0)
    except RuntimeError as run_time_error:
        logger.error(run_time_error)
        exit(0)
    except KeyboardInterrupt as keyboard_interrupt:
        logger.warning("KeyboardInterrupt")
        exit(0)

    # logger.info("started")
    # app.run(host=args.host, port=args.port)
