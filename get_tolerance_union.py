import os
import xml.etree.ElementTree as ET
import datetime
import pandas as pd
import numpy as np
import re

path = 'C:\Dev\Python\GetToleranceFromCsv\data\Ленинский\КПТ'

entity_spatial = '{urn://x-artefacts-rosreestr-ru/commons/complex-types/entity-spatial/5.0.1}'

source_path: str = os.path.join(os.path.normpath(path), 'xml')
output_path: str = os.path.join(os.path.normpath(path), 'data')

points_file_name = 'points'
input_xlsx_file = os.path.join(output_path, points_file_name + '.xlsx')
output_xlsx_file = os.path.join(output_path, points_file_name + '_output.xlsx')


def get_root_str(rt: ET.ElementTree) -> str:
    # Извлекаем строку для чтения данных не зависимо от типа фала xml
    # Получаем строку типа '{urn://x-artefacts-rosreestr-ru/outgoing/kvzu/7.0.1}'
    # print(re.search(r'(?<={)(?<someName>[^{}]+)(?=})', rt.tag))
    return rt.tag.split('}')[0] + '}'


def read_xml(output_xlsx: str) -> pd.DataFrame:
    table_out = []

    for file in os.listdir(source_path):
        if file.endswith(".xml"):
            tree = ''
            tree = ET.parse(os.path.join(source_path, file))
            root = ''
            root = tree.getroot()
            get_root = get_root_str(root)
            # print(get_root)
            for parcel in root.getiterator(get_root + 'Parcel'):
                cad_number = parcel.attrib['CadastralNumber']
                for point in parcel.getiterator(entity_spatial + 'SpelementUnit'):
                    point_num = point.attrib['SuNmb']
                    # print (str_parcel+point_num)
                    for coords in point.getiterator(entity_spatial + 'Ordinate'):
                        try:
                            delta = coords.attrib['DeltaGeopoint']
                        except KeyError:
                            delta = np.nan

                        row_table = {'Кадастровый номер участка': cad_number,
                                     'Номер точки': int(point_num),
                                     'X': float(coords.attrib['X']),
                                     'Y': float(coords.attrib['Y']),
                                     'Точность определения': float(delta)}
                        table_out.append(row_table)

    # Тут нужно вставить данные в датафрейм пандаса
    df_out = pd.DataFrame(table_out, columns=['Кадастровый номер участка',
                                                      'Номер точки',
                                                      'X',
                                                      'Y',
                                                      'Точность определения'])

    writer = pd.ExcelWriter(output_xlsx)
    df_out.to_excel(writer, na_rep='NaN')
    writer.save()

    return df_out


def read_xls_file(xls_file):
    return pd.read_excel(xls_file)


def row_count(data_frame, column=1):
    return data_frame.count(0)[column]


def get_tolerance(df: pd.DataFrame) -> pd.DataFrame:
    plots = df['Кадастровый номер участка'].unique()
    # plots.sort()

    table_out = []

    for plot in plots:
        # print(plot)

        df_plot = df.loc[df['Кадастровый номер участка'] == plot]
        # print(df_plot)

        df_plot = df_plot.replace(0, np.nan)  # Замена всех нулей на NaN в выбранном участке, что бы не мешали

        tolerance_min = df_plot['Точность определения'].min()
        tolerance_max = df_plot['Точность определения'].max()

        # print(f'Минимальная точность {tolerance_min}, максимальная точность {tolerance_max}.')

        # Заменяем NaN на нули (не уверен что это нужно)
        tolerance_min = 0 if np.isnan(tolerance_min) else tolerance_min
        tolerance_max = 0 if np.isnan(tolerance_max) else tolerance_max

        # Если в возвращаемом списке есть хотя бы одно пустое значение (NaN), то возвращаем 1
        tolerance_nan = 1 if len(df_plot[df_plot['Точность определения'].isnull()]) >= 1 else 0
        # print(df_plot[df_plot['Точность определения'].isnull()])

        row_table = {'Кадастровый номер участка': plot,
                     'Минпогрешность': tolerance_min,
                     'Макспогрешность': tolerance_max,
                     'Погрешность не определена': tolerance_nan}

        # print(row_table)

        table_out.append(row_table)

        # print('\n')

    df_out = pd.DataFrame(table_out, columns=['Кадастровый номер участка',
                                                      'Минпогрешность',
                                                      'Макспогрешность',
                                                      'Погрешность не определена'])

    return df_out


if __name__ == '__main__':
    time_start = datetime.datetime.now()

    df = read_xml(input_xlsx_file)

    data_frame_out = get_tolerance(df)

    writer = pd.ExcelWriter(output_xlsx_file)
    data_frame_out.to_excel(writer, sheet_name='Погрешность', na_rep='NaN', index=False)
    writer.save()

    time_end = datetime.datetime.now()
    print(f'\nВремя работы программы: {time_end - time_start}')
