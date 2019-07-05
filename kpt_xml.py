"""Этот модуль является первоначальным и использовался перед объединением.
На вход берет папку в которой есть папка XML с файлами. На выходе дает point.csv"""

import os
import xml.etree.ElementTree as ET
import datetime

SOURCE_PATH: str = "xml"
output_path: str = "data"

xmls = []
parcels = []
time_start = datetime.datetime.now()

for file in os.listdir(SOURCE_PATH):
    if file.endswith(".xml"):
        tree = ''
        tree = ET.parse(os.path.join(SOURCE_PATH, file))
        root = ''
        root = tree.getroot()
        xmls.append(os.path.join(SOURCE_PATH, file))
        # print("xml/"+file)
        for parcel in root.getiterator('{urn://x-artefacts-rosreestr-ru/outgoing/kpt/10.0.1}Parcel'):
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
                    parcels.append(cad_number + point_num + coord_parcel + delta)

# Тут нужно вставить данные в датафрейм пандаса

with open(os.path.join(output_path, "points.csv"), 'w') as f:
    for item in parcels:
        f.write("%s\n" % item)

time_end = datetime.datetime.now()
print(f'\nВремя работы программы: {time_end - time_start}')
