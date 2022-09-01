#!/usr/bin/python3
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import ScalarFormatter
import csv
import sys

data = {}

def generate(year, csv_file):
    with open(csv_file, newline='') as f:
        reader = csv.reader(f)
        first = True
        for row in reader:
            if first:
                first = False
            else:
                data[row[0]] = int(row[1])
    fig = plt.figure(tight_layout=True, figsize=[12.8, 9.6])
    ax = fig.subplots()
    data_sorted = dict(sorted(data.items(), key=lambda item: item[1], reverse=True))
    bars = ax.bar(data_sorted.keys(), data_sorted.values())
    ax.set_yscale('log')
    ax.bar_label(bars)
    ax.yaxis.set_major_formatter(ScalarFormatter())
    plt.title('{} commits by employer'.format(year))
    plt.ylabel('Commits')
    plt.setp(ax.get_xticklabels(), rotation=30, ha="right")
    plt.savefig("employers_bar.png", format='png')

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print("Usage {} <YEAR> <CSV Filename>".format(sys.argv[0]))
        exit(-1)
    generate(sys.argv[1], sys.argv[2])

