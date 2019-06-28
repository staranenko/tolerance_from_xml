from fuzzywuzzy import fuzz
import Levenshtein
import statistics as st
import pandas as pd
import numpy as np
import datetime


input_xls_file = 'data/adresses.xlsx'
output_xls_file = 'data/adresses_output.xlsx'


def compare(str1, str2):
    # токенизируем слова по пробелу - самый элементарный способ, хотя в модулях для natural language processing
    # (например, nltk) есть спец. токенизаторы
    print(str1 + ' - ' + str2)
    sentences = str1.split(), str2.split()
    # print(sentences)
    stats = {}
    res_levenshtein = []
    res_fuzzywuzzy = []
    res_jaro_winkler = []
    for w1, w2 in zip(sentences[0], sentences[1]):
        res_levenshtein.append(Levenshtein.ratio(w1, w2))
        res_fuzzywuzzy.append(fuzz.ratio(w1, w2))
        res_jaro_winkler.append(Levenshtein.jaro_winkler(w1, w2))

    stats['Levenshtein'] = st.mean(res_levenshtein)
    stats['fuzzywuzzy %'] = st.mean(res_fuzzywuzzy)
    stats['jaro_winkler'] = st.mean(res_jaro_winkler)

    # print('Levenshtein:', st.mean(res1))  # 0.8
    # print('fuzzywuzzy %:', st.mean(res2))  # 80
    # print('jaro_winkler:', st.mean(res3))  # 0.8796296296296297
    return stats


def read_xls_file(xls_file):
    return pd.read_excel(xls_file)


def row_count(data_frame, column=1):
    return data_frame.count(0)[column]


if __name__ == '__main__':
    time_start = datetime.datetime.now()

    df_xls = read_xls_file(input_xls_file)
    print(row_count(df_xls))

    addresses = [df_xls['Неформализ'], df_xls['Адрес_испр']]
    print(len(addresses))

    table_out = []

    for address in df_xls:
        print(address)
        stat_compare = compare(df_xls['Неформализ'], df_xls['Адрес_испр'])
    #
    #     row_table = {'Неформализ': address,
    #                  'Адрес_испр': address,
    #                  'Levenshtein': stat_compare['Levenshtein'],
    #                  'fuzzywuzzy %': stat_compare['fuzzywuzzy %'],
    #                  'jaro_winkler': stat_compare['jaro_winkler']}
    #
    #     table_out.append(row_table)
    #
    # data_frame_out = pd.DataFrame(table_out, columns=['Неформализ',
    #                                                   'Адрес_испр',
    #                                                   'Levenshtein',
    #                                                   'fuzzywuzzy %',
    #                                                   'jaro_winkler'])
    #
    # writer = pd.ExcelWriter(output_xls_file)
    # data_frame_out.to_excel(writer, sheet_name='Оценка', na_rep='NaN', index=False)
    # writer.save()

    time_end = datetime.datetime.now()

    print(f'\nВремя работы программы: {time_end - time_start}')

