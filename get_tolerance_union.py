import os
import xml.etree.ElementTree as ET
import datetime
import pandas as pd
import numpy as np
from pandas import DataFrame

path = 'C:\Dev\Python\GetToleranceFromCsv\data\Ленинский\ЗУ'

source_path: str = os.path.join(os.path.normpath(path), 'xml')
output_path: str = os.path.join(os.path.normpath(path), 'data')

points_file_name = 'points'
input_xlsx_file = os.path.join(output_path, points_file_name + '.xlsx')
output_xlsx_file = os.path.join(output_path, points_file_name + '_output.xlsx')


def read_xml(source: object, output: object, type_object: object = 'kpt') -> pd.DataFrame:
    xmls = []
    parcels = []
    table_out = []

    if type_object == 'kpt':
        get_root = '{urn://x-artefacts-rosreestr-ru/outgoing/kpt/10.0.1}'
    elif type_object == 'zu':
        get_root = '{urn://x-artefacts-rosreestr-ru/outgoing/kvzu/7.0.1}'

    for file in os.listdir(source_path):
        if file.endswith(".xml"):
            tree = ''
            tree = ET.parse(os.path.join(source_path, file))
            root = ''
            root = tree.getroot()
            xmls.append(os.path.join(source_path, file))
            # print("xml/"+file)
            for parcel in root.getiterator(get_root + 'Parcel'):
                str_parcel = ''
                cad_number = parcel.attrib['CadastralNumber'] + ','
                for point in parcel.getiterator(
                        '{urn://x-artefacts-rosreestr-ru/commons/complex-types/entity-spatial/5.0.1}SpelementUnit'):
                    point_num = point.attrib['SuNmb'] + ','
                    # print (str_parcel+point_num)
                    for coords in point.getiterator(
                            '{urn://x-artefacts-rosreestr-ru/commons/complex-types/entity-spatial/5.0.1}Ordinate'):
                        coord_parcel = coords.attrib['X'] + ',' + coords.attrib['Y'] + ','
                        try:
                            delta = coords.attrib['DeltaGeopoint']
                        except KeyError:
                            delta = 'NaN'
                        # print ('X:'+coords.attrib['X']+' Y:'+coords.attrib['Y']+' Delta:'+coords.attrib['DeltaGeopoint'])

                        row_table = {'Кадастровый номер участка': cad_number.split(',')[0],
                                     'Номер точки': point_num.split(',')[0],
                                     'X': coords.attrib['X'],
                                     'Y': coords.attrib['Y'],
                                     'Точность определения': delta}
                        #
                        table_out.append(row_table)
                        # print(row_table)
                        #
                        # parcels.append(cad_number + point_num + coord_parcel + delta)

    # Тут нужно вставить данные в датафрейм пандаса
    data_frame_out = pd.DataFrame(table_out, columns=['Кадастровый номер участка',
                                                      'Номер точки',
                                                      'X',
                                                      'Y',
                                                      'Точность определения'])

    writer = pd.ExcelWriter(input_xlsx_file)
    data_frame_out.to_excel(writer, na_rep='NaN')
    writer.save()

    # with open(os.path.join(output, os.path.join(output_path, points_file_name + '.csv')), 'w') as f:
    #     for item in parcels:
    #         f.write("%s\n" % item)
            
    return data_frame_out


def read_xls_file(xls_file):
    return pd.read_excel(xls_file)


def row_count(data_frame, column=1):
    return data_frame.count(0)[column]


def get_tolerance(df, output_xlsx) -> pd.DataFrame:
    # df_xls = read_xls_file(input_xlsx)
    # print(row_count(df_xls))

    plots = df['Кадастровый номер участка'].unique()
    # plots.sort()

    table_out = []

    for plot in plots:
        print(plot)

        df_plot = df.loc[df['Кадастровый номер участка'] == plot]
        print(df_plot)

        df_plot = df_plot.replace(0, np.nan)  # Замена всех нулей на NaN в выбранном участке

        tolerance_min = df_plot['Точность определения'].min()
        tolerance_max = df_plot['Точность определения'].max()

        print(f'Минимальная точность {tolerance_min}, максимальная точность {tolerance_max}.')

        # Заменяем NaN на нули
        # tolerance_min = 0 if np.isnan(tolerance_min) else tolerance_min
        tolerance_min = 0 if tolerance_min == 'NaN' else tolerance_min
        print(pd.isna(tolerance_min))
        # tolerance_max = 0 if np.isnan(tolerance_max) else tolerance_max
        tolerance_max = 0 if tolerance_max == 'NaN' else tolerance_max
        print('true' if tolerance_max == 'NaN' else 'false')


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

    # writer = pd.ExcelWriter(output_xlsx)
    # data_frame_out.to_excel(writer, sheet_name='Погрешность', na_rep='NaN', index=False)
    # writer.save()

    return data_frame_out


if __name__ == '__main__':
    time_start = datetime.datetime.now()

    df = read_xml(source_path, output_path, 'zu')  # zu/kpt

    data_frame_out = get_tolerance(df, output_xlsx_file)

    writer = pd.ExcelWriter(output_xlsx_file)
    data_frame_out.to_excel(writer, sheet_name='Погрешность', na_rep='NaN', index=False)
    writer.save()

    time_end = datetime.datetime.now()
    print(f'\nВремя работы программы: {time_end - time_start}')
