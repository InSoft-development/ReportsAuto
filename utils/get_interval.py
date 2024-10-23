import os
import errno
import argparse
import shutil
import json
import yaml

import pandas as pd
from loguru import logger

from typing import Union, Tuple, List

OBJECTS = f'objects{os.sep}'

CSV_PREDICT = f'csv_predict{os.sep}'
CSV_LOSS = f'csv_loss{os.sep}'
CSV_ROLL = f'csv_roll{os.sep}'
JSON_INTERVAL = f'json_interval{os.sep}'


def parse_args():
    parser = argparse.ArgumentParser(description="start interval detection")
    parser.add_argument("-s", "--source", type=str, help="specify source of experiment", required=True)
    parser.add_argument("-d", "--destination", type=str, help="specify destination directory "
                                                              "which will contain rolled csv and json intervals "
                                                              "by finded objects in experiment",
                        required=True)
    parser.add_argument("-c", "--config", type=str, help="specify config.yaml of experiment")
    return parser.parse_args()


def rolling_probability(df: pd.DataFrame, roll_in_hours: int, number_of_samples: int) -> pd.DataFrame:
    """
    Функция сглаживает вероятность target_value в фрейме
    :param df: фрейм с target_value
    :param roll_in_hours: сглаживание в часах
    :param number_of_samples: количество индексов в часе в фрейме
    :return: pd.DataFrame фрейм со сгаженным target_value
    """
    # Первые индексы после сглаживания будут Nan, запоминаем их
    temp_rows = df['target_value'].iloc[:roll_in_hours * number_of_samples]
    rolling_prob = df['target_value'].rolling(window=roll_in_hours * number_of_samples, min_periods=1).mean()
    rolling_prob.iloc[:roll_in_hours * number_of_samples] = temp_rows
    df['target_value'] = rolling_prob
    return df


def fill_zeros_with_last_value(df: pd.DataFrame, count_next: int = 288) -> None:
    """
    Процедура заполнения target_value при условии спада вероятности до нуля в сутках
    :param df: фрейм с target_value
    :param count_next: количество индексов в сутках в фрейме
    :return: None
    """
    count = 0
    for index, row in df.iterrows():
        if row['target_value'] == 0:
            if count == 0:
                start_index = index
                last_value = df.iloc[index - 1]['target_value']
            count += 1
        if row['target_value'] != 0 and count != 0:
            if count < count_next:
                df.loc[start_index:index - 1, 'target_value'] = last_value
            count = 0


def get_interval(target_value: pd.Series,
                 threshold_short: int,
                 threshold_long: int,
                 len_long: int,
                 len_short: int,
                 power: pd.Series,
                 power_limit: Union[int, float],
                 count_continue_short: int = 10,
                 count_continue_long: int = 15) -> Tuple[List[List[str]], List[Tuple[int, int]]]:
    """
    Функция выделения аномальных интервалов по параметрам постобработки
    :param target_value: серия target_value
    :param threshold_short: порог коротких интервалов
    :param threshold_long: порог длинных интервалов
    :param len_long: минимальное расстояние обнаружения длинного интервала
    :param len_short: минимальное расстояние обнаружения короткого интервала
    :param power: серия мощности power
    :param power_limit: отсечка по мощности
    :param count_continue_short: количество отсчетов для прерывания короткого интервала
    :param count_continue_long: количество отсчетов для прерывания длинного интервала
    :return: Кортеж из списка строк интервалов и списка кортежей индексов
    """
    long_interval_list = []
    short_interval_list = []
    target_value_interval = []
    count = 0
    i = 0
    long_idx_list = []
    short_idx_list = []
    sum_anomaly = 0
    for val in target_value:

        i += 1
        if val > threshold_long and check_power(power, i, power_limit):
            target_value_interval.append(val)
            count = 0
        else:
            count += 1
            target_value_interval.append(val)
            if count > count_continue_long:
                if len(target_value_interval) > len_long:
                    long_interval_list.append(target_value_interval)
                    if i - len(target_value_interval) > 0:
                        long_idx_list.append((i - len(target_value_interval), i))
                    else:
                        long_idx_list.append((0, i))
                    sum_anomaly += len(target_value_interval)
                count = 0
                target_value_interval.clear()
    i = 0
    for val in target_value:
        i += 1
        if val > threshold_short:
            target_value_interval.append(val)
            count = 0
        else:
            count += 1
            target_value_interval.append(val)
            if count > count_continue_short:
                if len(target_value_interval) > len_short:
                    isInLong = any(start <= i - len(target_value_interval) < end for start, end in long_idx_list)
                    if not isInLong:
                        short_interval_list.append(target_value_interval)
                        if i - len(target_value_interval) > 0:
                            short_idx_list.append((i - len(target_value_interval), i))
                        else:
                            short_idx_list.append((0, i))
                        sum_anomaly += len(target_value_interval)
                count = 0
                target_value_interval.clear()

    logger.info(f'Sum anomaly {sum_anomaly}, part of anomaly {round(sum_anomaly / len(target_value), 3)}')
    return long_interval_list + short_interval_list, long_idx_list + short_idx_list


def check_power(power: pd.Series, index: int, power_limit: Union[int, float],
                left_power_shift: int = 15, right_power_shift: int = 15) -> bool:
    """
    Функция проверки мощности на интервале для обрыва поиска аномального интервала
    :param power: серия мощности power
    :param index: текущий индекс поиска интервалов
    :param power_limit: отсечка по мощности
    :param left_power_shift: сдвиг влево индексов
    :param right_power_shift: сдвиг вправо индексов
    :return: True если хотя бы одно значение на интервале меньше отсечки по мощности
    """
    return any(val < power_limit for val in power[index - left_power_shift:right_power_shift + 15])


def main():
    try:
        args = parse_args()
    except SystemExit:
        logger.info("finished")
        exit(0)

    # Создание директории для сохранения объектов
    try:
        os.mkdir(os.path.join(args.destination, OBJECTS))
    except OSError as e:
        if e.errno != errno.EEXIST:
            logger.error(e)
            exit(0)

    # Считываем конфиг с константами и постобработкой
    with open(args.config, 'r') as read_file:
        config = yaml.safe_load(read_file)

    # Общее количество групп и счетчик группы для определения % выполнения
    groups_sum = sum([config[key]['count_of_groups'] if key != 'post_processing' else 0 for key in config])
    group_number = 0

    with open('complete.log', 'w') as write_file:
        write_file.write("0%")

    for object_directory in os.listdir(args.source):
        logger.info(object_directory)

        # Создание директорий для сохранения файлов
        data_path = os.path.join(OBJECTS, object_directory, 'data')
        try:
            os.mkdir(os.path.join(args.destination, os.path.join(OBJECTS, object_directory)))
        except OSError as e:
            if e.errno != errno.EEXIST:
                logger.error(e)
                exit(0)

        try:
            os.mkdir(os.path.join(args.destination, data_path))
        except OSError as e:
            if e.errno != errno.EEXIST:
                logger.error(e)
                exit(0)

        try:
            os.mkdir(os.path.join(args.destination, data_path, CSV_ROLL))
        except OSError as e:
            if e.errno != errno.EEXIST:
                logger.error(e)
                exit(0)

        try:
            os.mkdir(os.path.join(args.destination, data_path, JSON_INTERVAL))
        except OSError as e:
            if e.errno != errno.EEXIST:
                logger.error(e)
                exit(0)

        # Выделение интервалов
        # Проверяем равенство количества файлов предиктов и лоссов для групп
        predict_path = os.path.join(args.source, object_directory, CSV_PREDICT)
        loss_path = os.path.join(args.source, object_directory, CSV_LOSS)

        predict_len = len(os.listdir(predict_path))
        loss_len = len(os.listdir(loss_path))

        assert predict_len == loss_len, "count of predicts csv not equals count of loss csv"

        # Непосредственное выделение
        for i in range(config[object_directory]['count_of_groups']):
            predict = os.path.join(predict_path, f"predict_{i}.csv")
            loss = os.path.join(loss_path, f"loss_{i}.csv")
            roll = os.path.join(args.destination, data_path, f"{CSV_ROLL}roll_{i}.csv")
            json_interval = os.path.join(args.destination, data_path, f"{JSON_INTERVAL}group_{i}.json")

            # Копируем не сглаженный предикт в ролл, чтобы не изменять оригинал
            shutil.copy(predict, roll)

            roll_df = pd.read_csv(roll)

            # Сглаживание
            if config['post_processing']['roll_in_hours'] >= 0:
                roll_df = rolling_probability(roll_df, config['post_processing']['roll_in_hours'],
                                              config[object_directory]['number_of_sample'])

            # Заполняем пропуски нулями
            roll_df.fillna(value={"target_value": 0}, inplace=True)

            # Заполняем значениями, если есть спад вероятности в сутках
            fill_zeros_with_last_value(roll_df, count_next=24 * config[object_directory]['number_of_sample'])

            # Сохраняем сглаженный фрейм
            roll_df.to_csv(roll, index=False)

            # Подготовка фреймов к выделению интервалов
            roll_df.index = roll_df['timestamp']
            roll_df = roll_df.drop(columns=['timestamp'])

            loss_df = pd.read_csv(loss)
            loss_df.index = loss_df['timestamp']
            loss_df = loss_df.drop(columns=['timestamp'])

            # Фрейм с данными, из которой берем серию мощности
            power_df = pd.read_csv(config[object_directory]['data'], usecols=[config[object_directory]['power_index']])

            # Запуск выделения интервалов
            interval_list, idx_list = get_interval(target_value=roll_df['target_value'],
                                                   threshold_short=config['post_processing']['threshold_short'],
                                                   threshold_long=config['post_processing']['threshold_long'],
                                                   len_long=config['post_processing']['len_long'],
                                                   len_short=config['post_processing']['len_short'],
                                                   count_continue_short=config['post_processing'][
                                                       'count_continue_short'],
                                                   count_continue_long=config['post_processing']['count_continue_long'],
                                                   power=power_df[config[object_directory]['power_index']],
                                                   power_limit=config[object_directory]['power_limit'])

            # Формируем и сохраняем json-файл группы
            dict_list = []
            for j in idx_list:
                top_list = loss_df[j[0]:j[1]].mean().sort_values(ascending=False) \
                               .index[:config['post_processing']['count_top']].to_list()
                mean_measurement = list(
                    loss_df[j[0]:j[1]].mean().sort_values(ascending=False).values[:config['post_processing']['count_top']]
                )

                report_dict = {
                    "time": (str(roll_df.index[j[0]]), str(roll_df.index[j[1]])),
                    "len": j[1] - j[0],
                    "index": j,
                    "top_sensors": top_list,
                    "measurement": mean_measurement
                }
                dict_list.append(report_dict)

            with open(json_interval, "w") as json_write:
                json.dump(dict_list, json_write, indent=4)

            group_number += 1

            logger.info(f'{json_interval} has been saved')
            logger.info(f"{int(group_number / groups_sum * 100)}% completed")

            with open('complete.log', 'w') as write_file:
                write_file.write(f"{int(group_number / groups_sum * 100)}%")

    os.remove('complete.log')


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt as keyboard_interrupt:
        logger.warning("KeyboardInterrupt")
        pass
