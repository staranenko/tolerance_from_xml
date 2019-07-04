import os
import xml.etree.ElementTree as ET
import datetime
import pandas as pd
import numpy as np
import re
import tkinter as tk
from tkinter.ttk import Button, Label
from tkinter import filedialog, messagebox

PATH = ''
# path = '/home/tars/Dev/tolerance_from_xml/data/Ленинский/ЗУ/'
entity_spatial = '{urn://x-artefacts-rosreestr-ru/commons/complex-types/entity-spatial/5.0.1}'

# SOURCE_PATH: str = os.path.join(os.path.normpath(PATH), 'xml')
SOURCE_PATH: str = ''
# OUTPUT_PATH: str = os.path.join(os.path.normpath(PATH), 'data')
OUTPUT_PATH: str = ''

POINTS_FILE_NAME = 'points'
INPUT_XLSX_FILE = os.path.join(OUTPUT_PATH, POINTS_FILE_NAME + '.xlsx')
# OUTPUT_XLSX_FILE = os.path.join(OUTPUT_PATH, POINTS_FILE_NAME + '_output.xlsx')
OUTPUT_XLSX_FILE = ''


def get_root_str(rt: ET.ElementTree) -> str:
    """ Извлекаем строку для чтения данных не зависимо от типа фала xml
    Получаем строку типа '{urn://x-artefacts-rosreestr-ru/outgoing/kvzu/7.0.1}'"""

    re_my_exp = re.compile(r'(?<={)(?P<someName>[^{}]+)(?=})')
    result = re_my_exp.search(rt.tag).groupdict()
    return '{' + result['someName'] + '}'


def read_xml(output_xlsx: str, area) -> pd.DataFrame:
    table_out = []

    for file in os.listdir(SOURCE_PATH):
        if file.endswith(".xml"):
            tree = ''
            tree = ET.parse(os.path.join(SOURCE_PATH, file))
            root = ''
            root = tree.getroot()
            get_root = get_root_str(root)
            # app.insert_to_area(area, get_root, '\n')
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


def get_tolerance(df: pd.DataFrame, area) -> pd.DataFrame:
    plots = df['Кадастровый номер участка'].unique()
    plots.sort()

    table_out = []

    for plot in plots:
        # print(plot)

        df_plot = df.loc[df['Кадастровый номер участка'] == plot]
        print(df_plot)
        app.insert_to_area(area, df_plot, '\n')

        df_plot = df_plot.replace(0, np.nan)  # Замена всех нулей на NaN в выбранном участке, что бы не мешали

        tolerance_min = df_plot['Точность определения'].min()
        tolerance_max = df_plot['Точность определения'].max()

        print(f'Минимальная точность {tolerance_min}, максимальная точность {tolerance_max}.')
        app.insert_to_area(area, f'Минимальная точность {tolerance_min}, максимальная точность {tolerance_max}.', '\n')

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

        print(row_table)
        app.insert_to_area(area, row_table, '\n')

        table_out.append(row_table)

    df_out = pd.DataFrame(table_out, columns=['Кадастровый номер участка',
                                              'Минпогрешность',
                                              'Макспогрешность',
                                              'Погрешность не определена'])
    return df_out


class Application(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.initUI()
        self.center_window()

    def initUI(self):
        self.master.title("Извлечь точность точек из файлов XML (кадастр)")
        self.pack(fill=tk.BOTH, expand=True)
        self.master.minsize(width=500, height=300)

        self.columnconfigure(1, weight=1)
        self.columnconfigure(3, pad=7)
        self.rowconfigure(3, weight=1)
        self.rowconfigure(5, pad=7)

        lbl = Label(self, text="Папка с файлами XML")
        lbl.grid(sticky=tk.W, pady=4, padx=5)

        area = tk.Text(self)
        area.grid(row=1, column=0, columnspan=2, rowspan=4,
                  padx=5, sticky=tk.E + tk.W + tk.S + tk.N)
        area.config(state=tk.DISABLED)

        abtn = Button(self, text="Open Dir", command=lambda: self.onOpenDir(area))
        abtn.grid(row=1, column=3)

        hbtn = Button(self, text="Quit", command=self.master.destroy)
        hbtn.grid(row=5, column=0, padx=5)

        obtn = Button(self, text="Get Data", command=lambda: self.onGetData(area))
        obtn.grid(row=5, column=3)

    def center_window(self):
        w = 350
        h = 300

        sw = self.master.winfo_screenwidth()
        sh = self.master.winfo_screenheight()

        x = (sw - w) / 2
        y = (sh - h) / 2
        self.master.geometry('%dx%d+%d+%d' % (w, h, x, y))

    def onOpenDir(self, area):
        global PATH, SOURCE_PATH
        PATH = filedialog.askdirectory(title='Укажите папку с файлами XML', mustexist=True)
        if PATH != '':
            area.config(state=tk.NORMAL)
            area.delete(1.0, tk.END)
            area.insert(tk.END, PATH)
            area.config(state=tk.DISABLED)
            SOURCE_PATH = PATH

    def onGetData(self, area):
        global OUTPUT_PATH, INPUT_XLSX_FILE, OUTPUT_XLSX_FILE
        if PATH:
            fl = self.saveBox(title='Задайте файл для результата',
                              fileName='point_output',
                              fileExt='.xlsx',
                              fileTypes=[('XLSX files', '*.xlsx')])

            # print(fl)
            if fl:
                OUTPUT_XLSX_FILE = fl
                OUTPUT_PATH = os.path.dirname(fl)
                INPUT_XLSX_FILE = os.path.join(OUTPUT_PATH, POINTS_FILE_NAME + '.xlsx')

                self.insert_to_area(area, ['OUTPUT_PATH', OUTPUT_PATH])
                self.insert_to_area(area, ['OUTPUT_XLSX_FILE', OUTPUT_XLSX_FILE])
                self.insert_to_area(area, ['INPUT_XLSX_FILE', INPUT_XLSX_FILE])

                get_xml_data(area)
        else:
            messagebox.showerror('Ошибка', 'Не задана папака с файлами XML. Нажмите Open Dir и укажите размещение '
                                           'файлов.')

    def insert_to_area(self, area, val: object, sep='\n\t'):
        area.config(state=tk.NORMAL)
        area.insert(tk.END, [sep, val])
        area.config(state=tk.DISABLED)


    def saveBox(
            self,
            title=None,
            fileName=None,
            dirName=None,
            fileExt=".txt",
            fileTypes=None,
            asFile=False):
        self.master.update_idletasks()
        if fileTypes is None:
            fileTypes = [('all files', '.*'), ('text files', '.txt')]
        # define options for opening
        options = {}
        options['defaultextension'] = fileExt
        options['filetypes'] = fileTypes
        options['initialdir'] = dirName
        options['initialfile'] = fileName
        options['title'] = title

        if asFile:
            return filedialog.asksaveasfile(mode='w', **options)
        # will return "" if cancelled
        else:
            return filedialog.asksaveasfilename(**options)


def get_xml_data(area):
    time_start = datetime.datetime.now()
    app.insert_to_area(area, '\nОбработка начата...', '\n')

    df = read_xml(INPUT_XLSX_FILE, area)
    data_frame_out = get_tolerance(df, area)
    writer = pd.ExcelWriter(OUTPUT_XLSX_FILE)
    data_frame_out.to_excel(writer, sheet_name='Погрешность', na_rep='NaN', index=False)
    writer.save()

    time_end = datetime.datetime.now()
    app.insert_to_area(area, 'Обработка закончена.', '\n')
    app.insert_to_area(area, f'\nВремя работы программы: {time_end - time_start}')
    print(f'\nВремя работы программы: {time_end - time_start}')


if __name__ == '__main__':
    root = tk.Tk()
    app = Application(master=root)

    app.mainloop()
