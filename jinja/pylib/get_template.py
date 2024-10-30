from jinja2 import Environment, FileSystemLoader, BaseLoader

import time
import json
import os

from loguru import logger

import utils.constants_and_paths as constants
import utils.routine_operations as routine

from typing import Dict, Union, List
from flask_socketio import SocketIO
from pandas import DataFrame


def get_unfilled_html_from_source(content_for_render, url):
    logger.info(f"get_unfilled_html_from_source(content_for_render)")
    file_loader = FileSystemLoader(searchpath=constants.JINJA_TEMPLATE_SOURCE)
    env = Environment(loader=file_loader)
    tm = env.get_template('template.html')
    default_html = tm.render(content=content_for_render, url=url)
    return default_html


def get_render_common_report(socketio: SocketIO, slices: DataFrame, roll: DataFrame, kks_with_groups: DataFrame,
                             params: Dict[str, Union[str, int, List[dict], Dict[str, Union[str, List[str]]]]]) \
        -> Dict[str, str]:
    logger.info(f"get_render_common_report({socketio}, slices, roll, {params})")

    # Рендеринг общего отчета по частям

    # Формирование преамбулы отчеты
    preamble = {
        "text_object": f"Объект: {params['object']}",
        "text_group": f"Отчет по всем периодам группы {params['group']}"
    }

    # Формирование графика вероятности за весь период
    data_all, layout_all = routine.fill_plotly_interval_all(roll, params['object'], params['group'], params['interval'])
    main_chart = {
        "header": "График вероятности наступления аномалии за весь период",
        "variablePostfix": "Main",
        "id": "main",
        "data": data_all,
        "layout": json.dumps(layout_all)
    }

    # Рендеринг шаблона графика за весь период
    file_loader = FileSystemLoader(searchpath=constants.JINJA_TEMPLATE_CHARTS)
    env = Environment(loader=file_loader)
    tm = env.get_template('interval.html')
    main_chart_rendered = tm.render(chart=main_chart)

    socketio.emit("setPercentCommonReport", 20, to=params['sid'])

    # Формирование и рендеринг графиков вероятности за определенный интервал
    intervals_charts_rendered_list = [
        {
            "intervals_chart":  tm.render(chart={
                "header": "График вероятности наступления аномалии",
                "variablePostfix": f"Interval{i}",
                "id": f"interval-{i}",
                "data": data,
                "layout": json.dumps(layout)
            }),
            "multiples_axes_signals": [
                 routine.define_signals(kks_with_groups,
                                                   top,
                                                   params['power'],
                                                   params['palette']['main'],
                                                   params['palette']['power'],
                                                   params['palette']['other'])
                for j, top in enumerate(interval["top_sensors"])
            ],
            "multiples_axes_chart": [tm.render(chart={
                "header": top,
                "variablePostfix": f"MultiInterval{i}_{j}",
                "id": f"multi-interval-{i}-{j}",
                "data": multi_data,
                "layout": json.dumps(multi_layout)
            }) for j, top in enumerate(interval["top_sensors"])
                for multi_data, multi_layout in
                [routine.fill_plotly_multi_axes(slices, i,
                                                [record['kks'] for record in
                                                 routine.define_signals(kks_with_groups, top,
                                                                                   params['power'],
                                                                                   params['palette']['main'],
                                                                                   params['palette']['power'],
                                                                                   params['palette']['other'])],
                                                [record['kks'] for record in
                                                 routine.define_signals(kks_with_groups, top,
                                                                                   params['power'],
                                                                                   params['palette']['main'],
                                                                                   params['palette']['power'],
                                                                                   params['palette']['other'])],
                                                params['interval'],
                                                params={
                                                   'main_signal': top,
                                                   'power': params['power'],
                                                   'palette': params['palette']}
                                                )]
            ]
        }
        for i, interval in enumerate(params['interval'])
        for data, layout in
        [routine.fill_plotly_interval_specify(roll, params['object'], params['group'], i, params['interval'])]
    ]

    socketio.emit("setPercentCommonReport", 60, to=params['sid'])

    # Рендеринг шаблона отчета по всем интервалам
    file_loader = FileSystemLoader(searchpath=constants.JINJA_TEMPLATE_REPORTS)
    env = Environment(loader=file_loader)
    tm = env.get_template('interval_report.html')
    interval_report_rendered = tm.render(part_of_common_report=True, intervals=params['interval'],
                                         interval_chart=intervals_charts_rendered_list)

    socketio.emit("setPercentCommonReport", 70, to=params['sid'])

    # Рендеринг шаблона отчета по всем периодам группы
    # file_loader = FileSystemLoader(searchpath=constants.JINJA_TEMPLATE_REPORTS)
    # env = Environment(loader=file_loader)
    tm = env.get_template('common_report.html')
    common_report_rendered = tm.render(preamble=preamble, main_chart=main_chart_rendered,
                                       intervals=[interval['time'] for interval in params['interval']],
                                       interval_report=interval_report_rendered)

    socketio.emit("setPercentCommonReport", 80, to=params['sid'])

    # Рендеринг header, content, footer
    html = get_unfilled_html_from_source(common_report_rendered, params['url'])

    # socketio.emit("setPercentCommonReport", 0, to=params['sid'])
    # time.sleep(1)
    # socketio.emit("setPercentCommonReport", 50, to=params['sid'])
    # time.sleep(1)
    socketio.emit("setPercentCommonReport", 90, to=params['sid'])

    # logger.info(html)

    # Сохранение html
    with open(os.path.join(constants.OBJECTS + params['object'], constants.REPORTS_DIRECTORY,
                           f"common_report_{params['object']}.html"), "w") as write_html:
        write_html.write(html)

    socketio.emit("setPercentCommonReport", 100, to=params['sid'])

    return {'status': 'common report'}
