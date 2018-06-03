#!/usr/bin/python

# requerimientos: python3, scapy, numpy
import sys, os, argparse
from numpy import average,std
import csv

# from math import log as LOG
from scapy.all import *
from time import *

# Manejo de argumentos
parser = argparse.ArgumentParser(description='Implementacion en scapy de traceroute')
parser.add_argument('--destination-host', '-d', dest='host', default='google.com', help='host al cual se quiere hacer el traceroute (default: google.com)')
parser.add_argument('--ttl', '-t', dest='ttl',  type=int, default=30, help='ttl de los paquetes (default: 30)')
parser.add_argument('--queries', '-q', dest='queries',  type=int, default=1, help='numero de paquetes que se le envia a cada hop (default: 1)')
parser.add_argument('--timeout', '-o', dest='timeout', default=1, help='timeout del envio de cada paquete (default: 1s)')
parser.add_argument('--verbose', '-v', action='store_true', help='agregar si se desea verbosidad de la herramienta (default: no)')
parser.add_argument('--csv', '-c', dest='csv_file', default=None, help='agregar si se desea guardar los resultados para los rtts entre hops en un CSV')
args = parser.parse_args()

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

# Diccionario que para cada ttl, guarda una lista con tuplas (host, rtt)
responses = {}

ttl_range = range(1, args.ttl+1)

def get_route_stats(rs):
    table = {}
    last_rtt = 0
    for ttl in ttl_range:
        if ttl not in rs: continue

        # r = (src, rtt)
        ips = ",".join(list(set([ r[0] for r in rs[ttl] ])))
        avg_rtt = average( [ r[1] for r in rs[ttl] ] )
        std_rtt = std( [ r[1] for r in rs[ttl] ] )

        if avg_rtt-last_rtt<0.0:
            table[ttl] = (avg_rtt, std_rtt, 0, ips)
        else:
            table[ttl] = (avg_rtt, std_rtt, avg_rtt-last_rtt, ips)
            last_rtt = avg_rtt

    delta_rtts = [(ttl,table[ttl][2]) for ttl in table]
    avg_delta = average([delta for (_, delta) in delta_rtts])
    std_delta = std([delta for (_, delta) in delta_rtts], ddof=1)

    standardized_delta_rtts = map((lambda (ttl, delta): (ttl, (delta - avg_delta)/std_delta, delta)), delta_rtts)

    return table, list(standardized_delta_rtts)

def print_route(rs):
    table, _ = get_route_stats(rs)    
    print("ttl\tavg_rtt\tstd_rtt\td_rtt\tips")
    for ttl in ttl_range:
        if ttl not in table:
            print str(ttl) + '\t*\t*\t*\t*'
        else:
            # table[ttl] = (avg_rtt, std_rtt, delta_rtt, ips)
            print "%d\t" % (ttl) + "%.2f\t%.2f\t%.2f\t%s" % table[ttl]


# Recordar que se pueden invertir los siguientes ciclos.
dest_reached = False
for ttl in ttl_range:
    for i in range(args.queries):
        probe = IP(dst=args.host, ttl=ttl) / ICMP()

        t_i = time()
        # Envia un paquete, y devuelve la respuesta (si la hubo)
        ans = sr1(probe, verbose=False, timeout=float(args.timeout))
        t_f = time()

        if ans is not None:
            rtt = (t_f - t_i)*1000
            # Otra manera: el paquete enviado tiene su timestamp en sent_time, y el recibido en time. 
            #rtt = (ans.time - probe.sent_time)*1000

            if ttl not in responses: responses[ttl] = []
            responses[ttl].append((ans.src, rtt))

        os.system('clear')
        print "{host}, ttl={ttl}, iteracion {it}".format(host=args.host, ttl=ttl, it=i+1) 
        print_route( responses )

        # Tipo 0: echo-reply
        dest_reached = dest_reached or (ans is not None and ans.type==0)
    if dest_reached: break

_, z_scores = get_route_stats(responses)

if args.csv_file:
    with open(args.csv_file, 'w') as out_f:
        writer = csv.writer(out_f)
        for row in z_scores:
            writer.writerow(row)

print "z-scores:", z_scores
sample_size = len(z_scores)
print "tau:", tau_by_n[sample_size]

def outlier(z_score, sample_size):
    if sample_size in tau_by_n:
        return z_score > tau_by_n[sample_size]
    else:
        print "ATENCION: Muestra muy grande, utilizando maximo tau"
        return z_score > tau_by_n[float('inf')]

outliers_mask = list(map((lambda (ttl, z_score, delta): outlier(z_score, sample_size)), z_scores))

if not any(outliers_mask):
    print "No se detectaron enlaces intercontinentales"
else:
    for i in xrange(len(outliers_mask)):
        if outliers_mask[i]:
            print "Hay un enlace intercontinental en el salto", z_scores[i][0], "con z-score", z_scores[i][1]


            


