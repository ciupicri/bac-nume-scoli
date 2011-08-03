#!/usr/bin/env python
import csv
import difflib
import re

re_multiple_spaces = re.compile(r'''\s+''')
re_grup_scolar = re.compile(r'''GRUP(UL)? (SCOLAR)?''')
re_colegiu = re.compile(r'''COLEGIU(L)? (NATIONAL)? (DE)?''')
re_liceu = re.compile(r'''LICEU(L)? (TEORETIC)?''')

def get_canonical_school_name(s):
    return \
        re_liceu.sub('',
            re_colegiu.sub('',
                re_grup_scolar.sub('', 
                    re_multiple_spaces.sub(' ', s)))).strip()

data = {}
with open('/home/ciupicri/altii/irina/evolutie_licee.csv', 'rt') as f:
    csv_reader = csv.DictReader(f, delimiter=';')
    for i in csv_reader:
        data.setdefault(i['judet'], []).append(i)
        del i['judet']
        i['scoala_canonica'] = get_canonical_school_name(i['scoala'])
