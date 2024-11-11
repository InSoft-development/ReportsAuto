"""
Модуль содержит все использеумые в приложении константы
"""
import os

CONFIG = f'config.yaml'
CONFIG_BACKUP = f'config_backup.yaml'
CONFIG_STATION = f'config_station.yaml'
CONFIG_EXP = f'config_exp.yaml'

DATA_DIRECTORY = f'data{os.sep}'
DATA_CSV_ROLLED = f'{DATA_DIRECTORY}csv_roll{os.sep}'
DATA_JSON_INTERVAL = f'{DATA_DIRECTORY}json_interval{os.sep}'

JINJA = f'jinja{os.sep}'

JINJA_PYLIB = f'{JINJA}pylib{os.sep}'

JINJA_TEMPLATE = f'{JINJA}template{os.sep}'

JINJA_TEMPLATE_CHARTS = f'{JINJA_TEMPLATE}charts{os.sep}'
JINJA_TEMPLATE_CHARTS_INTERVAL = f'{JINJA_TEMPLATE_CHARTS}interval.html'

JINJA_TEMPLATE_REPORTS = f'{JINJA_TEMPLATE}reports{os.sep}'
JINJA_TEMPLATE_REPORTS_COMMON = f'{JINJA_TEMPLATE_REPORTS}common_report.html'
JINJA_TEMPLATE_REPORTS_INTERVAL = f'{JINJA_TEMPLATE_REPORTS}interval_report.html'
JINJA_TEMPLATE_REPORTS_PREAMBLE = f'{JINJA_TEMPLATE_REPORTS}preamble.html'

JINJA_TEMPLATE_SOURCE = f'{JINJA_TEMPLATE}source{os.sep}'
JINJA_TEMPLATE_SOURCE_HEADER = f'{JINJA_TEMPLATE_SOURCE}header.html'
JINJA_TEMPLATE_SOURCE_TEMPLATE = f'{JINJA_TEMPLATE_SOURCE}template.html'
JINJA_TEMPLATE_SOURCE_FOOTER = f'{JINJA_TEMPLATE_SOURCE}footer.html'

OBJECTS = f'objects{os.sep}'
OBJECTS_BACKUP = f'objects_backup{os.sep}'

PALETTE = {
    "main": '#1f77b4',
    "power": '#ff7f0e',
    "other": ['#2ca02c', '#d62728', '#9467bd']
}

REPORTS_DIRECTORY = f'reports{os.sep}'

STATIC_DIRECTORY = f'static{os.sep}'
STATIC_BOOTSTRAP_CSS_DIRECTORY = f'{STATIC_DIRECTORY}bootstrap{os.sep}dist{os.sep}css{os.sep}'
STATIC_BOOTSTRAP_JS_DIRECTORY = f'{STATIC_DIRECTORY}bootstrap{os.sep}dist{os.sep}js{os.sep}'
STATIC_PLOTLY_JS_DIRECTORY = f'{STATIC_DIRECTORY}plotly.js-dist{os.sep}'

WEB_DIR = f'web{os.sep}'
WEB_DIR_ASSETS = f'{WEB_DIR}assets{os.sep}'
WEB_DIR_ASSETS_INDEX_JS = f'{WEB_DIR_ASSETS}js{os.sep}'
WEB_API_URLS_JS = f'{WEB_DIR}api_urls.js'


