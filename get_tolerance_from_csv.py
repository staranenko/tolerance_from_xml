"""Этот модуль является первоначальным и использовался перед объединением.
На вход берет файл point.xlsx"""

import pandas as pd
import numpy as np
import datetime
import os


path = 'C:\Dev\Python\GetToleranceFromCsv\data\Ленинский\КПТ\data'

input_xls_file = os.path.join(os.path.normpath(path), 'points.xlsx')
output_xls_file = os.path.join(os.path.normpath(path), 'points_output.xlsx')


def read_xls_file(xls_file):
    return pd.read_excel(xls_file)


def row_count(data_frame, column=1):
    return data_frame.count(0)[column]


if __name__ == '__main__':
    time_start = datetime.datetime.now()

    df_xls = read_xls_file(input_xls_file)
    print(row_count(df_xls))

    plots = df_xls['Кадастровый номер участка'].unique()
    # plots.sort()

    table_out = []

    for plot in plots:
        print(plot)

        df_plot = df_xls.loc[df_xls['Кадастровый номер участка'] == plot]
        print(df_plot)

        df_plot = df_plot.replace(0, np.nan)  # Замена всех нулей на NaN в выбранном участке

        tolerance_min = df_plot['Точность определения'].min()
        tolerance_max = df_plot['Точность определения'].max()

        print(f'Минимальная точность {tolerance_min}, максимальная точность {tolerance_max}.')

        # Заменяем NaN на нули
        tolerance_min = 0 if np.isnan(tolerance_min) else tolerance_min
        tolerance_max = 0 if np.isnan(tolerance_max) else tolerance_max

        # Если в возвращаемом списке есть хотя бы одно не пустое значение (Nan), то возвращаем NaN
        # tolerance_nan = np.nan if len(df_plot[df_plot['Точность определения'].isnull()]) > 0 else ''
        tolerance_nan = 1 if len(df_plot[df_plot['Точность определения'].isnull()]) > 0 else 0
        # print(df_plot[df_plot['Точность определения'].isnull()])

        row_table = {'Кадастровый номер участка': plot,
                     'Минпогрешность': tolerance_min,
                     'Макспогрешность': tolerance_max,
                     'Погрешность не определена': tolerance_nan}

        # print(row_table)

        table_out.append(row_table)

        # print('\n')

    data_frame_out = pd.DataFrame(table_out, columns=['Кадастровый номер участка',
                                                      'Минпогрешность',
                                                      'Макспогрешность',
                                                      'Погрешность не определена'])

    writer = pd.ExcelWriter(output_xls_file)
    data_frame_out.to_excel(writer, sheet_name='Погрешность', na_rep='NaN', index=False)
    writer.save()

    time_end = datetime.datetime.now()

    print(f'\nВремя работы программы: {time_end - time_start}')

