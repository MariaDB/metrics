#!/usr/bin/python3
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.style as style
import matplotlib.ticker as ticker
import csv
import sys


date = []
new_prs = []
closed_prs = []
merged_prs = []

def generate(csv_file):
    with open(csv_file, newline='') as f:
        reader = csv.reader(f)
        first = True
        for row in reader:
            if first:
                first = False
            else:
                date.append(row[0])
                new_prs.append(int(row[1]))
                closed_prs.append(int(row[2]))
                merged_prs.append(int(row[3]))

    fig = plt.figure(tight_layout=True, figsize=[25.6, 19.2])

    width = 0.33
    style.use('fivethirtyeight')
    ax1 = fig.subplots()
    ax1.set_xlabel('Week Ending')
    ax1.set_ylabel('PR Count')
    ax1.yaxis.set_major_locator(ticker.MaxNLocator(integer=True))
    rects1 = ax1.plot(date, new_prs,label="New PRs")

    prs = {'Closed PRs': closed_prs, 'Merged PRs': merged_prs}

    ax2 = ax1.stackplot(date, prs.values(), labels=prs.keys(), alpha=0.5)
    ax1.legend()

    plt.setp(ax1.get_xticklabels(), rotation=30, ha="right")

    plt.savefig("prs.png", format='png')

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Usage {} <CSV Filename>".format(sys.argv[0]))
        exit(-1)
    generate(sys.argv[1])
