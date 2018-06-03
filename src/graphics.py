import pandas as pd
import argparse
import matplotlib.pyplot as plt
import os

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

def make_line_plot(df, tau, n, name):
	plt.subplot(2, 1, 1)
	plt.plot(df.ttl.values, df.delta.values, '.-')
	plt.ylabel('Delta RTT (ms)')
	plt.title('RTT entre hops')
	plt.xticks(xrange(1, df.ttl.max() + 2, 2))

	plt.subplot(2, 1, 2)
	plt.plot(df.ttl.values, df.z_score.values, '.-')
	plt.xlabel('TTL')
	plt.ylabel('Z-Score')
	plt.xticks(xrange(1, df.ttl.max() + 2, 2))

	ax = plt.gca()
	ax.hlines(tau, 1, df.ttl.max(), linestyle='--', linewidth=1, label=u'tau para n={}'.format(n), color='green')
	ax.legend()
	plt.savefig('{}.pdf'.format(name))	


parser = argparse.ArgumentParser(description='Implementacion en scapy de traceroute')
parser.add_argument('--filename', '-f', dest='filename')
args = parser.parse_args()

name = os.path.basename(args.filename).split('.')[0]

df = pd.read_csv(args.filename, sep='\t')
n = df.shape[0]
tau = tau_by_n[n]
make_line_plot(df, tau, n, name)
