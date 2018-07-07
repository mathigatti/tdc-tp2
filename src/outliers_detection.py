#!/usr/bin/python

import sys, os, argparse
from numpy import average,std
import csv
from operator import itemgetter

tau_by_n = {
    3: 1.1511,
    4: 1.4250,
    5: 1.5712,
    6: 1.6563,
    7: 1.7110,
    8: 1.7491,
    9: 1.7770,
    10: 1.7984,
    11: 1.8153,
    12: 1.8290,
    13: 1.8403,
    14: 1.8498,
    15: 1.8579,
    16: 1.8649,
    17: 1.8710,
    18: 1.8764,
    19: 1.8811,
    20: 1.8853,
    21: 1.8891,
    22: 1.8926,
    23: 1.8957,
    24: 1.8985,
    25: 1.9011,
    26: 1.9035,
    27: 1.9057,
    28: 1.9078,
    29: 1.9096,
    30: 1.9114,
    31: 1.9130,
    float('inf'): 1.9600
}

def find_greater_outlier(deltas):
    avg_delta = average([delta for (_, delta) in deltas])
    std_delta = std([delta for (_, delta) in deltas], ddof=1)
    z_scores = map((lambda (ttl, delta): (ttl, (delta - avg_delta)/std_delta, delta)), deltas)

    greater_outlier = max(z_scores, key=itemgetter(1))
    return greater_outlier if greater_outlier[1] > tau_by_n[len(deltas)] else None

parser = argparse.ArgumentParser(description='Implementacion del metodo de Cimbala')
parser.add_argument('--filename', '-f', dest='filename')
args = parser.parse_args()

deltas = []
with open(args.filename) as in_f:
    reader = csv.DictReader(in_f, delimiter='\t')
    for row in reader:
        t = (int(row['ttl']), float(row['delta']))
        if t[1] == 0.0:
            continue
        deltas.append(t)

outliers = []
greater_outlier = find_greater_outlier(deltas)

while greater_outlier is not None:
    outliers.append(greater_outlier)

    deltas.remove((greater_outlier[0], greater_outlier[2]))
    if len(deltas) < 3:
        break
    greater_outlier = find_greater_outlier(deltas)

if not outliers:
    print "No se detectaron enlaces intercontinentales"
else:
    for outlier in outliers:
        print "Hay un enlace intercontinental en el salto", outlier[0], "con z-score", outlier[1]