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


def get_render_common_report(socketio: SocketIO, slices: DataFrame, roll: DataFrame, loss: DataFrame,
                             kks_with_groups: DataFrame,
                             params: Dict[str, Union[str, int, List[dict], Dict[str, Union[str, List[str]]]]]) \
        -> Dict[str, str]:
    logger.info(f"get_render_common_report({socketio}, slices, roll, kks_with_groups, {params})")

    # Рендеринг общего отчета по частям
    # Формирование преамбулы отчеты
    preamble = {
        "text_object": f"Объект: {params['object']}",
        "text_group": f"Отчет по всем периодам группы {params['group']}"
    }

    # Формирование графика вероятности за весь период
    try:
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

    except Exception as interval_all_render_error:
        logger.error(interval_all_render_error)
        return {'error': str(interval_all_render_error)}

    socketio.emit("setPercentCommonReport", 20, to=params['sid'])

    # Рендеринг шаблона гистограммы распределения
    histogram_rendered = ""
    if params["group"] != 0:
        try:
            histogram_rendered = [tm.render(chart={
                "header": "Гистограмма распределения функции потерь датчиков (loss) "
                          "и вероятности возникновения аномалии (predict)",
                "variablePostfix": f"Histogram",
                "id": f"histogram",
                "data": data,
                "layout": json.dumps(layout)
            }) for data, layout in [routine.fill_plotly_histogram(loss,
                                                                  params['threshold_short'],
                                                                  params['threshold_long'])]][0]
        except Exception as histogram_render_error:
            logger.error(histogram_render_error)
            return {'error': str(histogram_render_error)}

    socketio.emit("setPercentCommonReport", 30, to=params['sid'])

    # Формирование и рендеринг графиков вероятности за определенный интервал
    try:
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
                                            params['palette']['other']) for top in interval["top_sensors"]
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

    except Exception as intervals_charts_render_error:
        logger.error(intervals_charts_render_error)
        return {'error': str(intervals_charts_render_error)}

    socketio.emit("setPercentCommonReport", 70, to=params['sid'])

    # Рендеринг шаблона отчета по всем периодам группы
    try:
        tm = env.get_template('common_report.html')
        common_report_rendered = tm.render(preamble=preamble, main_chart=main_chart_rendered,
                                           intervals=[interval['time'] for interval in params['interval']],
                                           interval_report=interval_report_rendered,
                                           histogram=histogram_rendered)
    except Exception as common_report_rendered_error:
        return {'error': str(common_report_rendered_error)}

    socketio.emit("setPercentCommonReport", 80, to=params['sid'])

    # Рендеринг header, content, footer
    try:
        html = get_unfilled_html_from_source(common_report_rendered, params['url'])

        # Сохранение html
        with open(os.path.join(constants.OBJECTS + params['object'], constants.REPORTS_DIRECTORY,
                               f"common_report_{params['object']}.html"), "w") as write_html:
            write_html.write(html)

    except Exception as html_render_error:
        logger.error(html_render_error)
        return {'error': str(html_render_error)}

    socketio.emit("setPercentCommonReport", 90, to=params['sid'])

    return {'status': 'common report'}


def get_render_interval_report(socketio: SocketIO, slices: DataFrame, roll: DataFrame, kks_with_groups: DataFrame,
                               tops: Dict[str, List[str]], others: Dict[str, List[str]],
                               params: Dict[str, Union[str, int, List[dict], Dict[str, Union[str, List[str]]]]]) \
        -> Dict[str, str]:
    logger.info(f"get_render_common_report({socketio}, slices, roll, kks_with_groups, {tops}, {others}, {params})")

    # Рендеринг общего отчета по частям
    # Формирование преамбулы отчеты
    preamble = {
        "text_object": f"Объект: {params['object']}",
        "text_group": f"Группа {params['group']}"
    }

    # Рендеринг шаблона графика на итервале
    try:
        file_loader = FileSystemLoader(searchpath=constants.JINJA_TEMPLATE_CHARTS)
        env = Environment(loader=file_loader)
        tm = env.get_template('interval.html')

        socketio.emit("setPercentIntervalReport", 20, to=params['sid'])

        intervals_charts_rendered_list = [
            {
                "intervals_chart": tm.render(chart={
                    "header": "График вероятности наступления аномалии",
                    "variablePostfix": f"Interval",
                    "id": f"interval",
                    "data": data,
                    "layout": json.dumps(layout)
                }),
                "multiples_axes_top_signals": [
                    routine.define_signals(kks_with_groups,
                                           top,
                                           params['power'],
                                           params['palette']['main'],
                                           params['palette']['power'],
                                           params['palette']['other'],
                                           tops[top]["activeSignals"]) for top in tops.keys()
                ],
                "multiples_axes_other_signals": [
                    routine.define_signals(kks_with_groups,
                                           other,
                                           params['power'],
                                           params['palette']['main'],
                                           params['palette']['power'],
                                           params['palette']['other'],
                                           others[other]["activeSignals"]) for other in others.keys()
                ],
                "multiples_axes_top_chart": [
                    tm.render(chart={
                        "header": top,
                        "variablePostfix": f"MultiIntervalTop{i}",
                        "id": f"multi-interval-top-{i}",
                        "data": multi_data,
                        "layout": json.dumps(multi_layout)
                    }) for i, top in enumerate(tops.keys())
                    for multi_data, multi_layout in [
                        routine.fill_plotly_multi_axes(slices, params['interval_num'],
                                                       tops[top]["signals"],
                                                       tops[top]["activeSignals"],
                                                       params['interval'],
                                                       params={
                                                           'main_signal': top,
                                                           'power': params['power'],
                                                           'palette': params['palette']
                                                       })
                    ]
                ],
                "multiples_axes_other_chart": [
                    tm.render(chart={
                        "header": other,
                        "variablePostfix": f"MultiIntervalOther{i}",
                        "id": f"multi-interval-other-{i}",
                        "data": multi_data,
                        "layout": json.dumps(multi_layout)
                    }) for i, other in enumerate(others.keys())
                    for multi_data, multi_layout in [
                        routine.fill_plotly_multi_axes(slices, params['interval_num'],
                                                       others[other]["signals"],
                                                       others[other]["activeSignals"],
                                                       params['interval'],
                                                       params={
                                                           'main_signal': other,
                                                           'power': params['power'],
                                                           'palette': params['palette']
                                                       })
                    ]
                ],
            }
            for data, layout in [routine.fill_plotly_interval_specify(roll, params['object'], params['group'],
                                                                      params['interval_num'], params['interval'])]
        ]
    except Exception as intervals_charts_render_error:
        logger.error(intervals_charts_render_error)
        return {'error': str(intervals_charts_render_error)}

    socketio.emit("setPercentIntervalReport", 80, to=params['sid'])

    # Рендеринг шаблона отчета интервала
    try:
        file_loader = FileSystemLoader(searchpath=constants.JINJA_TEMPLATE_REPORTS)
        env = Environment(loader=file_loader)
        tm = env.get_template('interval_report.html')
        interval_report_rendered = tm.render(part_of_common_report=False, preamble=preamble,
                                             intervals=[params['interval'][params['interval_num']]],
                                             interval_chart=intervals_charts_rendered_list,
                                             tops=tops, others=others)
    except Exception as interval_report_render_error:
        logger.error(interval_report_render_error)
        return {'error': str(interval_report_render_error)}

    # Рендеринг header, content, footer
    try:
        html = get_unfilled_html_from_source(interval_report_rendered, params['url'])

        # Сохранение html
        with open(os.path.join(constants.OBJECTS + params['object'], constants.REPORTS_DIRECTORY,
                               f"interval_report_{params['interval_num']}.html"), "w") as write_html:
            write_html.write(html)
    except Exception as html_render_error:
        logger.error(html_render_error)
        return {'error': str(html_render_error)}

    socketio.emit("setPercentIntervalReport", 90, to=params['sid'])

    return {'status': 'interval report'}
