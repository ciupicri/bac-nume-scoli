#!/usr/bin/env python
import collections
import csv, codecs, cStringIO
import difflib
import re

class UTF8Recoder:
    """
    Iterator that reads an encoded stream and reencodes the input to UTF-8
    """
    def __init__(self, f, encoding):
        self.reader = codecs.getreader(encoding)(f)

    def __iter__(self):
        return self

    def next(self):
        return self.reader.next().encode("utf-8")

class UnicodeReader:
    """
    A CSV reader which will iterate over lines in the CSV file "f",
    which is encoded in the given encoding.
    """

    def __init__(self, f, dialect=csv.excel, encoding="utf-8", **kwds):
        f = UTF8Recoder(f, encoding)
        self.reader = csv.reader(f, dialect=dialect, **kwds)

    def next(self):
        row = self.reader.next()
        return [unicode(s, "utf-8") for s in row]

    def __iter__(self):
        return self

Scoala = collections.namedtuple('Scoala',
        ('scoala', 'judet', 'new_id',
            'nota_medie_2006', 'rank_2006',
            'nota_medie_2007', 'rank_2007',
            'nota_medie_2008', 'rank_2008',
            'nota_medie_2009', 'rank_2009',
            'nota_medie_2010', 'rank_2010',
            'nota_medie_2011', 'rank_2011'))

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
with open('/home/ciupicri/altii/irina/evolutie_licee.csv', 'rb') as f:
    csv_reader = UnicodeReader(f, delimiter=';')
    for i in csv_reader:
        i = Scoala(*i)
        scoala_canonica = get_canonical_school_name(i.scoala)
        data.setdefault(i.judet, {}).setdefault(scoala_canonica, [])\
                .append(i)

new_data = {}
for judet, scoli in data.items():
    L = []
    scoli_canonice = scoli.keys()
    while scoli_canonice:
        scoala_canonica = scoli_canonice.pop()
        matches = difflib.get_close_matches(scoala_canonica, scoli_canonice,
                                            n=6, cutoff=0.9)
        group = scoli[scoala_canonica]
        for i in matches:
            group.extend(scoli[i])
        L.append(group)
    new_data[judet] = L
