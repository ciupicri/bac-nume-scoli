#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
import collections
import csv, codecs, cStringIO
import difflib
import logging
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
re_grup_scolar = re.compile(r'''GRUP(UL)? (SCOLAR)? (INDUSTRIAL)?''')
re_colegiu = re.compile(r'''COLEGIU(L)? (NATIONAL)? (DE)?''')
re_liceu = re.compile(r'''LICEU(L)? (TEORETIC)?''')

def get_canonical_school_name(s):
    return \
        re_liceu.sub('',
            re_colegiu.sub('',
                re_grup_scolar.sub('',
                    re_multiple_spaces.sub(' ',
                        s.upper()\
                                .replace(u'Â', 'A')\
                                .replace(u'Ă', 'A')\
                                .replace(u'Î', 'I')\
                                .replace(u'Ș', 'S')\
                                .replace(u'Ț', 'T')\
                        )))).strip()

class MergeConflict(Exception):
    pass

def merge_group(group):
    L = []
    for values in zip(*[i[3:] for i in group]):
        values = list(values)
        value = None
        while values:
            x = values.pop()
            if x != 'NA':
                value = x
                break
        while values:
            x = values.pop()
            if x != 'NA':
                raise MergeConflict()
        if value is None:
            logging.warn("No value found in group %s" % (repr(group), ))
        L.append(value)
    nume_scoala = [i.scoala for i in group if i.nota_medie_2011!='NA']
    judet = group[0].judet
    return Scoala(nume_scoala, judet, None, *L)

def get_data(filename):
    data = {}
    with open(filename, 'rb') as f:
        csv_reader = UnicodeReader(f, delimiter=';')
        for i in csv_reader:
            i = Scoala(*i)
            scoala_canonica = get_canonical_school_name(i.scoala)
            data.setdefault(i.judet, {}).setdefault(scoala_canonica, [])\
                    .append(i)
    return data

def group_data(data):
    grouped_data = {}
    for judet, scoli in data.items():
        groups = []
        scoli_canonice = scoli.keys()
        while scoli_canonice:
            scoala_canonica = scoli_canonice.pop()
            matches = difflib.get_close_matches(scoala_canonica, scoli_canonice,
                                                n=6, cutoff=0.9)
            group = scoli[scoala_canonica]
            for i in matches:
                group.extend(scoli[i])
            groups.append(group)
        grouped_data[judet] = groups
    return grouped_data

def merge_data(data):
    merged_data = {}
    for judet, groups in data.items():
        for group in groups:
            try:
                scoala = merge_group(group)
            except:
                logging.exception("Merge conflict for group %s" % (repr(group), ))
            merged_data.setdefault(judet, []).append(scoala)
    return merged_data

logging.basicConfig()
data = get_data('/home/ciupicri/altii/irina/evolutie_licee.csv')
grouped_data = group_data(data)
merged_data = merge_data(grouped_data)
