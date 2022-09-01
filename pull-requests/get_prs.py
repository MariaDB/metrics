#!/usr/bin/python3

import requests
import json
import datetime
import time
import os
import sys


GITHUB_TOKEN = os.environ['GITHUB_TOKEN']

auth_header = {'Authorization': 'token ' + GITHUB_TOKEN}

idx = (datetime.datetime.today().weekday() + 1) % 7
sun = datetime.datetime.today() - datetime.timedelta(idx)

def call_github(url):
    request = requests.get(url, headers = auth_header)

    if request.status_code != 200:
        print("Failed to get PR count")
        exit()

    pr_data = json.loads(request.text)
    count = pr_data['total_count']
    # Avoid 30 requests per minute limit
    time.sleep(2)
    return count

def generate(start_wn, end_wn):
    filename = "prs-{}..{}.csv".format(start_wn, end_wn)
    f = open(filename, "w")
    f.write('Week Ending,New PRs,Closed PRs,Merged PRs,Total PRs,Still Open PRs\n')

    begin_date = datetime.datetime.strptime(start_wn + '-1', "%Y-W%W-%w")
    finish_date = datetime.datetime.strptime(end_wn + '-1', "%Y-W%W-%w")
    if finish_date > sun:
        finish_date = sun

    current_date = begin_date
    while current_date < finish_date :
        start_date = current_date.strftime('%Y-%m-%d')
        end_date = (current_date + datetime.timedelta(days=6.9)).strftime('%Y-%m-%d')
        print("Processing {} - {}".format(start_date, end_date))
        totals_end_date = (current_date + datetime.timedelta(days=7.9)).strftime('%Y-%m-%d')
        open_url = 'https://api.github.com/search/issues?q=repo:MariaDB/server%20is:pr%20created:' + start_date + '..' + end_date + '&per_page=1'
        closed_url = 'https://api.github.com/search/issues?q=repo:MariaDB/server%20is:pr%20is:closed%20closed:' + start_date + '..' + end_date + '&per_page=1'
        merged_url = 'https://api.github.com/search/issues?q=repo:MariaDB/server%20is:pr%20is:merged%20closed:' + start_date + '..' + end_date + '&per_page=1'

        total_open_url = 'https://api.github.com/search/issues?q=repo:MariaDB/server%20is:pr%20created:<' + totals_end_date + '&per_page=1'
        total_close_url = 'https://api.github.com/search/issues?q=repo:MariaDB/server%20is:pr%20closed:<' + totals_end_date + '&per_page=1'

        open_count = call_github(open_url)
        close_count = call_github(closed_url)
        merged_count = call_github(merged_url)
        total_open_count = call_github(total_open_url)
        total_close_count = call_github(total_close_url)

        f.write('{},{},{},{},{},{}\n'.format(end_date, open_count, close_count - merged_count, merged_count, total_open_count, total_open_count - total_close_count))
        current_date = current_date + datetime.timedelta(days=7)
    f.close()

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print("Usage {} <START_WN> <END_WN>\n".format(sys.argv[0]))
        print("Where the WN parameters are in the format 2022-W04 for week 4 of 2022\n")
        exit(-1)
    generate(sys.argv[1], sys.argv[2])

