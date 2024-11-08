from flask import Flask, request, jsonify, send_file, send_from_directory, Response
from flask_cors import CORS
from flask_socketio import SocketIO
from flask.helpers import send_file

import os
import argparse
import time
import shutil
import copy
import json
import yaml

import subprocess
import signal

from bs4 import BeautifulSoup as bs
import pandas as pd

import datetime
from dateutil.parser import parse

import re

import utils.constants_and_paths as constants
import utils.correct_deploy as deploy
import utils.routine_operations as routine

import jinja.pylib.get_template as template

from loguru import logger
import gevent

from typing import Dict, List

VERSION = '1.0.0'

config_path = None
config = None
config_backup = None

app = Flask(__name__, static_folder="./web", template_folder="./web", static_url_path="")
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')
clients = {}

# Переменная под фрейм исходных данных срезов
slices_df = None
# Переменная под фрейм kks, групп и описания
kks_with_groups = None
# Переменная под фрейм сглаженных данных
roll_df = None
# Переменная под фрейм предикта
predict_df = None
# Переменная под фрейм лосса
loss_df = None
# Переменная под json интервалы
json_interval = None


# Переменная под объект процесса Popen выделения интервалов
p_get_interval = None
sid_proc = None
# Переменная под объект гринлета построения отчета
report_greenlet = None


@socketio.on("connect")
def connect() -> None:
    """
    Процедура регистрирует присоединение нового клиента и открытие сокета
    :return: None
    """
    clients[request.sid] = request.sid
    logger.info("connect")
    logger.info(request.sid)


@socketio.on("disconnect")
def disconnect() -> None:
    """
    Процедура регистрирует разъединение клиента и закрытие сокета
    :return: None
    """
    del clients[request.sid]
    logger.info("disconnect")
    logger.info(request.sid)


@app.route("/", defaults={"path": ""})
@app.route("/<string:path>")
@app.route("/<path:path>")
def catch_all(path):
    """
    Функция посылки index.html
    :param path: путь URL, начинаюющийся с /
    :return: index.html
    """
    return app.send_static_file("index.html")


@app.route('/api_urls.js')
def get_api_urls_js():
    """
    Функция посылки js файла с URL бэкенда
    :return: ./web/api_urls.js
    """
    return send_file('./web/api_urls.js')


@app.route('/bootstrap/dist/css/bootstrap.min.css')
def get_bootstrap_css():
    """
    Функция запроса файла bootstrap.css
    :return: Возвращает файл bootstrap.css в header html
    """
    logger.info(f"get_bootstrap_css()")
    logger.info(f"get style {constants.STATIC_BOOTSTRAP_CSS_DIRECTORY}bootstrap.css")
    return send_from_directory(constants.STATIC_BOOTSTRAP_CSS_DIRECTORY, 'bootstrap.min.css')


@app.route('/bootstrap/dist/js/bootstrap.bundle.min.js')
def get_bootstrap_js():
    """
    Функция запроса скрипта bootstrap.bundle.min.js
    :return: Возвращает скрипт bootstrap.bundle.min.js в html
    """
    logger.info(f"get_bootstrap_js()")
    logger.info(f"get script {constants.STATIC_BOOTSTRAP_JS_DIRECTORY}bootstrap.bundle.min.js")
    return send_from_directory(constants.STATIC_BOOTSTRAP_JS_DIRECTORY, 'bootstrap.bundle.min.js')


@app.route('/plotly.js-dist-min/plotly.js')
def get_plotly_js():
    """
    Функция запроса скрипта plotly.js
    :return: Возвращает скрипт plotly.js в html
    """
    logger.info(f"get_plotly_js()")
    logger.info(f"get script {constants.STATIC_PLOTLY_JS_DIRECTORY}plotly.js")
    return send_from_directory(constants.STATIC_PLOTLY_JS_DIRECTORY, 'plotly.js')


@app.route("/common_report.html")
def get_common_report_html():
    """
    Функция посылки общего отчета html по всей группе
    :return: Возвращает отчет в виде интерактивного html
    """
    logger.info("get_common_report_html()")
    object_selected = request.args.get('objectSelected', type=str)
    return send_file(os.path.join(constants.OBJECTS + object_selected, constants.REPORTS_DIRECTORY,
                                  f"common_report_{object_selected}.html"))


@app.route("/common_report.pdf")
def get_common_report_pdf():
    """
    Функция посылки общего отчета html по всей группе
    :return: Возвращает отчет в виде pdf
    """
    logger.info("get_common_report_pdf()")
    object_selected = request.args.get('objectSelected', type=str)
    return send_file(os.path.join(constants.OBJECTS + object_selected, constants.REPORTS_DIRECTORY,
                                  f"common_report_{object_selected}.pdf"))


@app.route("/interval_report.html")
def get_interval_report_html():
    """
    Функция посылки отчета html по интервалу
    :return: Возвращает отчет в виде интерактивного html
    """
    logger.info("get_interval_report_html()")
    object_selected = request.args.get('objectSelected', type=str)
    active_interval = request.args.get('activeInterval', type=int)
    return send_file(os.path.join(constants.OBJECTS + object_selected, constants.REPORTS_DIRECTORY,
                                  f"interval_report_{active_interval}.html"))


@app.route("/interval_report.pdf")
def get_interval_report_pdf():
    """
    Функция посылки отчета pdf по интервалу
    :return: Возвращает отчет в виде pdf
    """
    logger.info("get_interval_report_pdf()")
    object_selected = request.args.get('objectSelected', type=str)
    active_interval = request.args.get('activeInterval', type=int)
    return send_file(os.path.join(constants.OBJECTS + object_selected, constants.REPORTS_DIRECTORY,
                                  f"interval_report_{active_interval}.pdf"))


@app.route('/api/init_sidebar/', methods=['GET'])
def init_sidebar() -> Response:
    global slices_df, kks_with_groups, roll_df, loss_df, json_interval
    logger.info(f"init_sidebar()")
    # Инициализируем исходные интервалы
    json_interval = init_json_interval
    # Инициализируем pandas фреймы
    slices_df = pd.read_csv(config_path[init_object]['slices'], parse_dates=['timestamp'], index_col=['timestamp'])
    kks_with_groups = pd.read_csv(config_path[init_object]['kks_with_groups'], sep=';')
    # Убираем Nan-ы в описании датчиков
    kks_with_groups['name'].fillna(value='ОПИСАНИЯ НЕТ', inplace=True)
    roll_df = pd.read_csv(os.path.join(config_path[init_object]['roll'], f'roll_{init_group}.csv'), parse_dates=['timestamp'], index_col=['timestamp'])
    loss_df = pd.read_csv(os.path.join(config_path[init_object]['loss'], f'loss_{init_group}.csv'), parse_dates=['timestamp'], index_col=['timestamp'])

    return jsonify(object=init_object, objects=init_objects, group=init_group, groups=init_groups,
                   intervals=init_intervals)


@app.route('/api/update_sidebar/', methods=['GET'])
def update_sidebar() -> Response:
    def update_sidebar_by_object(ob: str, gr: int) -> Response:
        global slices_df, kks_with_groups, roll_df, loss_df, json_interval
        logger.info(f"update_sidebar_by_object({ob}, {gr})")
        # Загружаем необходимые pandas фреймы при смене объекта
        slices_df = pd.read_csv(config_path[object_selected]['slices'], parse_dates=['timestamp'], index_col=['timestamp'])
        kks_with_groups = pd.read_csv(config_path[object_selected]['kks_with_groups'], sep=';')
        # Убираем Nan-ы в описании датчиков
        kks_with_groups['name'].fillna(value='ОПИСАНИЯ НЕТ', inplace=True)
        roll_df = pd.read_csv(os.path.join(config_path[object_selected]['roll'], f'roll_{group}.csv'), parse_dates=['timestamp'], index_col=['timestamp'])
        loss_df = pd.read_csv(os.path.join(config_path[object_selected]['loss'], f'loss_{group}.csv'), parse_dates=['timestamp'], index_col=['timestamp'])

        with open(os.path.join(config_path[object_selected]['json_interval'], f'group_{group}.json'), 'r') as read_file:
            json_interval = json.load(read_file)
        intervals = [record['time'] for record in json_interval]

        return jsonify(intervals=intervals, group=group, groups=groups)

    def update_sidebar_by_group(ob: str, gr: int) -> Response:
        global roll_df, loss_df, json_interval
        logger.info(f"update_sidebar_by_group({ob}, {gr})")
        # Загружаем необходимые pandas фреймы при смене группы
        roll_df = pd.read_csv(os.path.join(config_path[object_selected]['roll'], f'roll_{group}.csv'), parse_dates=['timestamp'], index_col=['timestamp'])
        loss_df = pd.read_csv(os.path.join(config_path[object_selected]['loss'], f'loss_{group}.csv'), parse_dates=['timestamp'], index_col=['timestamp'])

        with open(os.path.join(config_path[object_selected]['json_interval'], f'group_{group}.json'), 'r') as read_file:
            json_interval = json.load(read_file)
        intervals = [record['time'] for record in json_interval]

        return jsonify(intervals=intervals, group=group, groups=groups)

    update_sidebar_cause_dict = {
        'object': update_sidebar_by_object,
        'group': update_sidebar_by_group
    }

    object_selected = request.args.get('objectSelected', type=str)
    group_selected = request.args.get('groupSelected', type=int)
    cause = request.args.get('cause', type=str)
    logger.info(f"update_sidebar({object_selected}, {group_selected}, {cause})")

    groups = config[object_selected]['count_of_groups']
    group = group_selected if group_selected < groups else 0
    logger.info(f"update_sidebar({object_selected}, {group})")

    return update_sidebar_cause_dict[cause](object_selected, group)


@app.route('/api/init_post_processing/', methods=['GET'])
def init_post_processing() -> Response:
    logger.info(f"init_post_processing()")
    return jsonify(postProcessing=routine.dict_to_lower_camel_case(config['post_processing']))


@socketio.on('/api/interval_detection/')
def interval_detection(post_processing: dict) -> Dict[str, str]:
    global config, config_backup, p_get_interval, sid_proc
    sid = request.sid
    if p_get_interval is not None:
        return {'causeException': "Процесс уже запущен для другого клиента", 'status': 'error'}
    sid_proc = sid
    logger.info(f"interval_detection({post_processing})")

    post_processing = routine.dict_to_snake_case(post_processing)
    # Временное сохранение директорий объектов и конфига на случай отмены выделения интервалов
    config_backup = copy.deepcopy(config)
    routine.copy_recursively_objects_directory(constants.OBJECTS, constants.OBJECTS_BACKUP)

    # Сохраняем параметры, на которых выделяем интервал, в конфиг
    config['post_processing'] = post_processing
    with open(constants.CONFIG, 'w') as write_file:
        yaml.dump(config, write_file)

    # Считываем конфиг с константами и постобработкой
    with open(constants.CONFIG, 'r') as read_file:
        config = yaml.safe_load(read_file)

    # Запуск выделения интервалов, если ошибка, то восстанавливаем исходный конфиг и директории с объектами
    arguments = ["python", "./get_interval.py", "-s", args.path, "-d", os.getcwd(),
                 "-c", os.path.join(os.getcwd(), constants.CONFIG)]
    logger.info(' '.join(arguments))
    try:
        p_get_interval = subprocess.Popen(arguments, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                          cwd=os.path.join(os.getcwd(), 'utils'))
        while p_get_interval.poll() is None:
            socketio.sleep(2)
            if os.path.isfile(f'utils{os.sep}complete.log'):
                with open(f'utils{os.sep}complete.log', 'r') as read_file:
                    status = read_file.readline()
                    logger.info(status)
                    socketio.emit("setPercentIntervalDetection", int(status.strip('%')), to=sid)
    except subprocess.CalledProcessError as subprocess_exception:
        logger.error(subprocess_exception)
        # Восстанавливаем исходный конфиг и объекты
        config = routine.backup_recovery(constants.CONFIG, config_backup, constants.OBJECTS_BACKUP,
                                         constants.OBJECTS)
        return {'causeException': str(subprocess_exception), 'status': 'error'}
    except RuntimeError as run_time_error:
        logger.error(run_time_error)
        # Восстанавливаем исходный конфиг и объекты
        config = routine.backup_recovery(constants.CONFIG, config_backup, constants.OBJECTS_BACKUP,
                                         constants.OBJECTS)
        return {'causeException': str(run_time_error), 'status': 'error'}
    except KeyboardInterrupt as keyboard_interrupt:
        logger.warning("KeyboardInterrupt")
        # Восстанавливаем исходный конфиг и объекты
        config = routine.backup_recovery(constants.CONFIG, config_backup, constants.OBJECTS_BACKUP,
                                         constants.OBJECTS)
        return {'causeException': str(keyboard_interrupt), 'status': 'error'}

    # Интервалы успешно выделились - бекап не нужен, удаляем временную директорию
    logger.info("p_get_interval finished")
    # Восстанавливаем исходный конфиг и объекты, если процесс завершился с ошибкой или был прерван
    return_code = p_get_interval.returncode
    if return_code != 0:
        config = routine.backup_recovery(constants.CONFIG, config_backup, constants.OBJECTS_BACKUP, constants.OBJECTS)
        p_get_interval = None
        return {'causeException': f"код завершения процесса {return_code}", 'status': 'success'}
    routine.remove_recursively_objects_directory(constants.OBJECTS_BACKUP)

    # Удаляем старые html и pdf отчеты и создаем заново директорию reports в objects
    routine.remove_reports(constants.OBJECTS)
    p_get_interval = None
    return {'status': 'success'}


@socketio.on('/api/cancel_interval_detection/')
def interval_detection_cancel() -> Dict[str, str]:
    global config, p_get_interval, sid_proc
    sid = request.sid

    if sid_proc != sid:
        return {'status': 'error'}

    logger.info(f"interval_detection_cancel()")
    if p_get_interval.poll() is None:
        p_get_interval.terminate()
        sid_proc = None
        logger.info("p_get_interval canceled")
    return {'status': 'success'}


@app.route('/api/update_plotly_interval/', methods=['GET'])
def update_plotly_interval() -> Response:
    def update_plotly_interval_all() -> Response:
        global roll_df, json_interval
        logger.info(f"update_plotly_interval_all()")
        # Заполняем данные графика
        data, layout = routine.fill_plotly_interval_all(roll_df, object_selected, group_selected, json_interval)
        return jsonify(data=data, layout=layout)

    def update_plotly_interval_specify(interval_num: int) -> Response:
        global roll_df, json_interval
        logger.info(f"update_plotly_interval_specify({interval_num})")
        data, layout = routine.fill_plotly_interval_specify(roll_df, object_selected, group_selected, interval_num,
                                                            json_interval)
        return jsonify(data=data, layout=layout)

    object_selected = request.args.get('objectSelected', type=str)
    group_selected = request.args.get('groupSelected', type=int)
    interval_selected = request.args.get('intervalSelected', type=str)

    logger.info(f"update_plotly_interval({object_selected}, {group_selected}, {interval_selected})")
    return update_plotly_interval_all() if interval_selected == 'all' else update_plotly_interval_specify(int(interval_selected))


@app.route('/api/get_signals/', methods=['GET'])
def get_signals() -> Response:
    object_selected = request.args.get('objectSelected', type=str)
    group_selected = request.args.get('groupSelected', type=int)
    interval_selected = request.args.get('intervalSelected', type=str)

    logger.info(f"get_signals({object_selected}, {group_selected}, {interval_selected})")
    top_list = json_interval[int(interval_selected)]["top_sensors"]
    other_list = kks_with_groups.loc[kks_with_groups['group'] == group_selected]['kks'].tolist()
    # Убираем повторы с топовыми датчиками
    other_list = list(set(other_list) - set(top_list))

    top_list_descr = kks_with_groups.loc[kks_with_groups['kks'].isin(top_list)]['name'].tolist()
    other_list_descr = kks_with_groups.loc[kks_with_groups['kks'].isin(other_list)]['name'].tolist()

    return jsonify(top=[{'kks': kks, 'description': descr} for kks, descr in zip(top_list, top_list_descr)],
                   other=[{'kks': kks, 'description': descr} for kks, descr in zip(other_list, other_list_descr)])


@app.route('/api/get_additional_signals/', methods=['GET'])
def get_additional_signals() -> Response:
    main_signal_kks = request.args.get('mainSignal', type=str)
    object_selected = request.args.get('objectSelected', type=str)

    logger.info(f"get_additional_signals({main_signal_kks}, {object_selected})")
    return jsonify(additionalSignals=routine.define_additional_signals(kks_with_groups,
                                                                       main_signal_kks,
                                                                       config[object_selected]['power_index'],
                                                                       constants.PALETTE['power'],
                                                                       constants.PALETTE['other']))


@app.route('/api/update_plotly_multiple_axes/', methods=['GET'])
def update_plotly_multiple_axes() -> Response:
    global slices_df, json_interval
    main_signal_kks = request.args.get('mainSignal', type=str)
    object_selected = request.args.get('objectSelected', type=str)
    interval_selected = request.args.get('intervalSelected', type=int)
    signals = request.args.getlist('signals[]')
    active_signals = request.args.getlist('activeCheckbox[]')

    logger.info(f"update_plotly_multiple_axes({main_signal_kks}, {object_selected}, {interval_selected}, {signals}, {active_signals})")

    signals.insert(0, main_signal_kks)

    if not signals:
        return jsonify(data=[], layout=[])

    # Упорядочиваем по списку порядок выбора чекбоксов сигнала
    active_signals = [signal for signal in signals if signal in active_signals]
    data, layout = routine.fill_plotly_multi_axes(slices_df, interval_selected,
                                                  signals, active_signals, json_interval,
                                                  params={
                                                      'main_signal': main_signal_kks,
                                                      'power': config[object_selected]['power_index'],
                                                      'palette': constants.PALETTE})
    return jsonify(data=data, layout=layout)


@app.route('/api/update_plotly_histogram/', methods=['GET'])
def update_plotly_histogram() -> Response:
    global loss_df
    logger.info(f"update_plotly_histogram()")

    data, layout = routine.fill_plotly_histogram(loss_df,
                                                 config['post_processing']['threshold_short'],
                                                 config['post_processing']['threshold_long'])

    return jsonify(data=data, layout=layout)


@socketio.on('/api/common_report/')
def common_report(object_selected: str, group_selected: int) -> Dict[str, str]:
    global slices_df, roll_df, loss_df, kks_with_groups
    sid = request.sid
    logger.info(f"common_report({object_selected}, {group_selected})")

    params = {
        'url': f"http://{args.host}:{args.port}/",
        'sid': sid,
        'object': object_selected,
        'group': group_selected,
        'interval': json_interval,
        'power': config[object_selected]['power_index'],
        'palette': constants.PALETTE,
        'threshold_short': config['post_processing']['threshold_short'],
        'threshold_long': config['post_processing']['threshold_long']
    }

    return template.get_render_common_report(socketio, slices_df, roll_df, loss_df, kks_with_groups, params)


@socketio.on('/api/interval_report/')
def interval_report(object_selected: str, group_selected: int, interval_selected: int,
                    tops_order: List[str], others_order: List[str], active_signals: Dict[str, Dict[str, List[str]]]) -> Dict[str, str]:
    global slices_df, roll_df, kks_with_groups
    sid = request.sid
    logger.info(f"interval_report({object_selected}, {group_selected}, {interval_selected}, "
                f"{tops_order}, {others_order}, {active_signals})")

    params = {
        'url': f"http://{args.host}:{args.port}/",
        'sid': sid,
        'object': object_selected,
        'group': group_selected,
        'interval': json_interval,
        'interval_num': interval_selected,
        'power': config[object_selected]['power_index'],
        'palette': constants.PALETTE
    }

    # Упорядочивание по списку многоосевых графиков
    active_signals_order = {
        "top": {top: active_signals["top"][top] for top in tops_order if top in active_signals["top"].keys()},
        "other": {other: active_signals["other"][other] for other in others_order if other in active_signals["other"].keys()}
    }

    logger.info(active_signals_order)
    return template.get_render_interval_report(socketio, slices_df, roll_df, kks_with_groups,
                                               active_signals_order["top"], active_signals_order["other"],
                                               params)


def parse_args():
    parser = argparse.ArgumentParser(description="start flask + vue 3 ReportAuto web-application")
    parser.add_argument("-p", "--path", type=str, help="specify path of experiment", required=True)
    parser.add_argument("-ip", "--host", type=str, help="specify IPv4 address of host", required=True)
    parser.add_argument("-po", "--port", type=int, help="specify port", required=True)
    parser.add_argument("-i", "--ignore", default=False, help="flag of ignore of initial detection of intervals",
                        required=False, action="store_true")
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

    # Запуск первоначального выделения интервалов, если в опциях не передан флаг на игнорирование
    if not args.ignore:
        arguments = ["python", "./get_interval.py", "-s", args.path, "-d", os.getcwd(),
                     "-c", os.path.join(os.getcwd(), constants.CONFIG)]
        logger.info(' '.join(arguments))
        try:
            p_get_interval_init = subprocess.Popen(arguments, stdout=subprocess.PIPE,
                                                   cwd=os.path.join(os.getcwd(), 'utils'))
            p_get_interval_init.wait()
        except subprocess.CalledProcessError as subprocess_exception:
            logger.error(subprocess_exception)
            exit(0)
        except RuntimeError as run_time_error:
            logger.error(run_time_error)
            exit(0)
        except KeyboardInterrupt as keyboard_interrupt:
            logger.warning("KeyboardInterrupt")
            exit(0)

    # Перезаполняем в bundle версии файл api_urls.js для настройки проксирования
    with open(constants.WEB_API_URLS_JS, 'r') as read_file:
        api_file = read_file.read()
        replacement_string = re.search("\'(.*)\'", api_file).group()
        api_file = api_file.replace(replacement_string, f"'http://{args.host}:{args.port}/'")
    with open(constants.WEB_API_URLS_JS, 'w') as write_file:
        write_file.write(str(api_file))

    # Инициализируем объекты станций и количество групп для старта бэкенда на Flask
    init_objects = list(config_path.keys())
    init_object = init_objects[0]
    init_group = 0
    init_groups = config[init_object]['count_of_groups']
    with open(os.path.join(config_path[init_object]['json_interval'], f'group_{init_group}.json'), 'r') as read_file:
        init_json_interval = json.load(read_file)
    init_intervals = [record['time'] for record in init_json_interval]
    json_interval = init_json_interval

    # Инициализируем pandas фреймы
    slices_df = pd.read_csv(config_path[init_object]['slices'], parse_dates=['timestamp'], index_col=['timestamp'])
    kks_with_groups = pd.read_csv(config_path[init_object]['kks_with_groups'], sep=';')
    # Убираем Nan-ы в описании датчиков
    kks_with_groups['name'].fillna(value='ОПИСАНИЯ НЕТ', inplace=True)
    roll_df = pd.read_csv(os.path.join(config_path[init_object]['roll'], f'roll_{init_group}.csv'), parse_dates=['timestamp'], index_col=['timestamp'])
    loss_df = pd.read_csv(os.path.join(config_path[init_object]['loss'], f'loss_{init_group}.csv'), parse_dates=['timestamp'], index_col=['timestamp'])

    logger.info("started")
    # app.run(host=args.host, port=args.port)
    socketio.run(app, host=args.host, port=args.port)
