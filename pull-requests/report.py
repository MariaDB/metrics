#!/usr/bin/python3

import datetime
import argparse
import pr_github as gh

# Using globals here, only because there is no threads.
# Don't do this, don't be like me :)
verbose = False
days = None
prsort = None
limit = 30

def generate(sort):
    if verbose:
        print("\nGetting report data", end='')

    now = datetime.datetime.now(datetime.timezone.utc)
    url = 'https://api.github.com/search/issues?q=repo:MariaDB/server%20is:pr%20is:open%20-is%3Adraft%20sort:created-' + sort + '&per_page=100'
    pr_data = gh.get_paginated_data(url, verbose)
    pr_info = []
    for pr_list in pr_data:
        for pr in pr_list['items']:
            pr_updated = datetime.datetime.fromisoformat(pr['updated_at'])
            if (now - pr_updated).days > days:
                pr_info.append({"pr": pr['number'], "days": (now - pr_updated).days})

    if prsort == 'shortest':
        pr_info.sort(key=lambda x:x['days'])
    elif prsort == 'longest':
        pr_info.sort(key=lambda x:x['days'], reverse=True)

    counter = 0
    f = open("report.csv", "w")
    f.write('PR Number,Last Updated Days Ago,URL\n')
    for pr in pr_info:
        f.write('{},{},https://github.com/MariaDB/server/pull/{}\n'.format(pr['pr'], pr['days'], pr['pr']))
        counter = counter + 1
        if limit > 0 and counter >= limit:
            break
    f.close()
    print('\nReport generated as report.csv. Found ' + str(len(pr_info)) + ' items, ' + str(counter) + ' written to CSV file')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
            prog='report',
            description='Generate reports for pull requests that require attention')
    parser.add_argument('-r', '--report', required=True, choices=['old', 'new'], help='Type of report to generate.\n\'old\' is the oldest pull requests that have had no action in X days.\n\'new\' is the newest pull requests that have had no action in X days.')
    parser.add_argument('-v', '--verbose', action=argparse.BooleanOptionalAction)
    parser.add_argument('-d', '--days', type=int, default=7, help='Number of days since last action on PR (default 7)')
    parser.add_argument('-l', '--limit', type=int, default=30, help='Maximum number of items for report, 0 = unlimited, default 30')
    parser.add_argument('-s', '--sort', choices=['longest', 'shortest'], help='Sort by longest or shortest time since first response')
    args = parser.parse_args()
    verbose = args.verbose
    limit = args.limit
    days = args.days
    prsort = args.sort

    match args.report:
        case 'old':
            generate('asc')
        case 'new':
            generate('desc')




