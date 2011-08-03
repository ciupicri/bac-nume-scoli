#!/usr/bin/env python
import csv
import difflib
import re

re_multiple_spaces = re.compile(r'''\s+''')

with open('/home/ciupicri/altii/irina/evolutie_licee.csv', 'rt') as f:
    csv_reader = csv.DictReader(f, delimiter=';')
    licee = [i for i in csv_reader]

data = {}
for i in licee:
    data.setdefault(i['judet'], []).append(i)
    del i['judet']
    i['scoala_canonica'] = re_multiple_spaces.sub(' ', i['scoala'])\
            .replace('GRUP SCOLAR', '')\
            .replace('GRUPUL SCOLAR', '')\
            .replace('COLEGIU NATIONAL', '')\
            .replace('COLEGIUL NATIONAL', '')\
            .replace('COLEGIUL', '')\
            .replace('LICEUL TEORETIC', '')\
            .replace('LICEUL', '')

del licee
