#!/usr/bin/python3

import requests
import json
import datetime
import time
import os
import re
import sys

GITHUB_TOKEN = os.environ['GITHUB_TOKEN']

auth_header = {'Authorization': 'token ' + GITHUB_TOKEN}

idx = (datetime.datetime.today().weekday() + 1) % 7
sun = datetime.datetime.today() - datetime.timedelta(idx)
user_list = []

def get_paginated_data(url):
    data = []
    while(True):
        response = requests.get(url, headers = auth_header)
        if response.status_code != 200:
            print("Failed to get json data")
            exit()
        # TODO: calculate backoff better using all the headers given
        if (int(response.headers['X-RateLimit-Remaining']) <= 5):
            print('_', end='')
            time.sleep(2)
        else:
            print('.', end='')
        sys.stdout.flush()
        data.append(json.loads(response.text))
        try:
            groups = re.search(r"<([^<]*)>; rel=\"next\"", response.headers['Link'])
            url = groups.group(1)
        except:
            break
    return data

def get_json_data(url):
    response = requests.get(url, headers = auth_header)
    if response.status_code != 200:
        print("Failed to get json data")
        exit()
    if (int(response.headers['X-RateLimit-Remaining']) <= 5):
        print('_', end='')
        time.sleep(2)
    else:
        print('.', end='')
    sys.stdout.flush()

    return json.loads(response.text)

def call_get_users():
    print("Getting users", end='')
    url = 'https://api.github.com/orgs/MariaDB/members'
    user_data = get_paginated_data(url)
    for user_pages in user_data:
        for user in user_pages:
            user_list.append(user['login'])
    print("Done!")

def parse_comments(comment_data, review_data, user):
    comment_date = None
    review_date = None
    for comment_list in comment_data:
        for comment in comment_list:
            if user != comment['user']['login'] and comment['user']['login'] in user_list:
                comment_date = comment['created_at']
                break
        if comment_date is not None:
            break
    for review_list in review_data:
        for review in review_list:
            if user != review['user']['login'] and review['user']['login'] in user_list:
                review_date = review['submitted_at']
                break
        if review_date is not None:
            break

    if review_date is None:
        if comment_date is None:
            return None
        else:
            return comment_date
    else:
        if comment_date is None:
            return review_date
        else:
            c_date = datetime.datetime.fromisoformat(comment_date)
            r_date = datetime.datetime.fromisoformat(review_date)
            if c_date < r_date:
                return comment_date
            else:
                return review_date
    return None


def call_first_response(url):
    pr_data = get_paginated_data(url)
    pr_info = []
    counters = {'total_days': 0, 'with_comments': 0, 'without_comments': 0}
    for pr_list in pr_data:
        for pr in pr_list['items']:
            pr_info.append({"pr": pr['number'], "user": pr['user']['login'], "created_at": pr['created_at']})

    for pr in pr_info:
        url = "https://api.github.com/repos/MariaDB/server/issues/" + str(pr['pr']) + "/comments"
        comments_data = get_paginated_data(url)
        url = "https://api.github.com/repos/MariaDB/server/pulls/" + str(pr['pr']) + "/reviews"
        review_data = get_paginated_data(url)
        comment_date = parse_comments(comments_data, review_data, pr['user'])
        if comment_date is not None:
            # TODO: Calculate days from date
            pr_date = datetime.datetime.fromisoformat(pr['created_at'])
            c_date = datetime.datetime.fromisoformat(comment_date)
            counters['total_days'] = counters['total_days'] + (c_date - pr_date).days
            counters['with_comments'] = counters['with_comments'] + 1
        else:
            counters['without_comments'] = counters['without_comments'] + 1

    return counters

def call_github(url):
    pr_data = get_json_data(url)
    count = pr_data['total_count']
    return count

def generate(start_wn, end_wn):
    call_get_users()
    # Special case, ottok review shouldn't count but in list
    user_list.remove("ottok")

    filename = "prs-{}..{}.csv".format(start_wn, end_wn)
    f = open(filename, "w")
    f.write('Week Ending,New PRs,Closed PRs,Merged PRs,Total PRs,Still Open PRs,Days to first response,New PRs responded,New PRs not responded\n')

    begin_date = datetime.datetime.strptime(start_wn + '-1', "%Y-W%W-%w")
    finish_date = datetime.datetime.strptime(end_wn + '-1', "%Y-W%W-%w")
    if finish_date > sun:
        finish_date = sun

    current_date = begin_date
    while current_date < finish_date :
        start_date = current_date.strftime('%Y-%m-%d')
        end_date = (current_date + datetime.timedelta(days=6.9)).strftime('%Y-%m-%d')
        print("Processing {} - {}".format(start_date, end_date), end='')
        totals_end_date = (current_date + datetime.timedelta(days=7.9)).strftime('%Y-%m-%d')
        open_url = 'https://api.github.com/search/issues?q=repo:MariaDB/server%20is:pr%20created:' + start_date + '..' + end_date + '&per_page=1'
        closed_url = 'https://api.github.com/search/issues?q=repo:MariaDB/server%20is:pr%20is:closed%20closed:' + start_date + '..' + end_date + '&per_page=1'
        merged_url = 'https://api.github.com/search/issues?q=repo:MariaDB/server%20is:pr%20is:merged%20closed:' + start_date + '..' + end_date + '&per_page=1'

        total_open_url = 'https://api.github.com/search/issues?q=repo:MariaDB/server%20is:pr%20created:<' + totals_end_date + '&per_page=1'
        total_close_url = 'https://api.github.com/search/issues?q=repo:MariaDB/server%20is:pr%20closed:<' + totals_end_date + '&per_page=1'
        first_response_url = 'https://api.github.com/search/issues?q=repo:MariaDB/server%20is:pr%20created:' + start_date + '..' + end_date + '&per_page=100'

        open_count = call_github(open_url)
        close_count = call_github(closed_url)
        merged_count = call_github(merged_url)
        total_open_count = call_github(total_open_url)
        total_close_count = call_github(total_close_url)
        first_response = call_first_response(first_response_url)

        if first_response['with_comments']:
            average_response = round(first_response['total_days'] / first_response['with_comments'], 1)
        else:
            average_response = "NULL"
        f.write('{},{},{},{},{},{},{},{},{}\n'.format(end_date, open_count, close_count - merged_count, merged_count, total_open_count, total_open_count - total_close_count, average_response, first_response['with_comments'], first_response['without_comments']))
        current_date = current_date + datetime.timedelta(days=7)
        print("Done!")
    f.close()

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print("Usage {} <START_WN> <END_WN>\n".format(sys.argv[0]))
        print("Where the WN parameters are in the format 2022-W04 for week 4 of 2022\n")
        exit(-1)
    generate(sys.argv[1], sys.argv[2])

