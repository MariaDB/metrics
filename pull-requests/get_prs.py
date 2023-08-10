#!/usr/bin/python3

import datetime
import argparse
import pr_github as gh


idx = (datetime.datetime.today().weekday() + 1) % 7
sun = datetime.datetime.today() - datetime.timedelta(idx)
user_list = []
verbose = False


def call_get_users():
    print("Getting users", end='')
    url = 'https://api.github.com/orgs/MariaDB/members'
    user_data = gh.get_paginated_data(url, verbose)
    for user_pages in user_data:
        for user in user_pages:
            user_list.append(user['login'])
    if verbose:
        print(" Found " + str(len(user_list)) + " users")
    else:
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
    pr_data = gh.get_paginated_data(url, verbose)
    pr_info = []
    counters = {'total_days': 0, 'with_comments': 0, 'without_comments': 0, 'uncounted': 0, 'self_merge': 0}
    for pr_list in pr_data:
        for pr in pr_list['items']:
            pr_info.append({"pr": pr['number'], "user": pr['user']['login'], "created_at": pr['created_at'], "closed_at": pr['closed_at']})

    if verbose:
        print(" Processing PR list")
    for pr in pr_info:
        if verbose:
            print("PR: " + str(pr['pr']), end='')
        url = "https://api.github.com/repos/MariaDB/server/issues/" + str(pr['pr']) + "/comments"
        comments_data = gh.get_paginated_data(url, verbose)
        url = "https://api.github.com/repos/MariaDB/server/pulls/" + str(pr['pr']) + "/reviews"
        review_data = gh.get_paginated_data(url, verbose)
        comment_date = parse_comments(comments_data, review_data, pr['user'])
        if comment_date is not None:
            pr_date = datetime.datetime.fromisoformat(pr['created_at'])
            c_date = datetime.datetime.fromisoformat(comment_date)
            counters['total_days'] = counters['total_days'] + (c_date - pr_date).days
            counters['with_comments'] = counters['with_comments'] + 1
            if verbose:
                print(" first meaningful comment " + str((c_date - pr_date).days) + " days")
        else:
            close_data = gh.get_json_data("https://api.github.com/repos/MariaDB/server/issues/" + str(pr['pr']), verbose)
            #print(pr['pr'])
            if close_data["state"] == "closed" and "closed_by" in close_data and close_data['user']['login'] == close_data['closed_by']['login']:
                # Self merge with no developer comments
                if close_data['pull_request']['merged_at'] is not None:
                    counters['self_merge'] = counters['self_merge'] + 1
                    if verbose:
                        print(" was merged by author with no meaningful comments")
                # Self closed with no developer comments
                else:
                    counters['uncounted'] = counters['uncounted'] + 1
                    if verbose:
                        print(" was closed by author with no meaningful comments")
            else:
                counters['without_comments'] = counters['without_comments'] + 1
                if verbose:
                    print(" has had no meaningful comments yet")

    return counters

def call_github(url):
    pr_data = gh.get_json_data(url, verbose)
    count = pr_data['total_count']
    return count

def generate(start_wn, end_wn):
    call_get_users()
    # Special case, ottok review shouldn't count but in list
    try:
        user_list.remove("ottok")
    except:
        if verbose:
            print("Failed to remove Otto from list")

    filename = "prs-{}..{}.csv".format(start_wn, end_wn)
    f = open(filename, "w")
    f.write('Week Ending,New PRs,Draft PRs,Closed PRs,Merged PRs,Total PRs,Still Open PRs,Days to First Response,New PRs Responded,New PRs Not Responded,PRs Self Merge No Review,PRs Self Closed No Review\n')

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
        draft_url = 'https://api.github.com/search/issues?q=repo:MariaDB/server%20is%3Adraft%20created:' + start_date + '..' + end_date + '&per_page=1'

        total_open_url = 'https://api.github.com/search/issues?q=repo:MariaDB/server%20is:pr%20created:<' + totals_end_date + '&per_page=1'
        total_close_url = 'https://api.github.com/search/issues?q=repo:MariaDB/server%20is:pr%20closed:<' + totals_end_date + '&per_page=1'
        first_response_url = 'https://api.github.com/search/issues?q=repo:MariaDB/server%20is:pr%20-is%3Adraft%20created:' + start_date + '..' + end_date + '&per_page=100'

        if verbose:
            print("\nGetting open count", end='')
        open_count = call_github(open_url)
        if verbose:
            print(" Found " + str(open_count) + "\nGetting close count", end='')
        close_count = call_github(closed_url)
        if verbose:
            print(" Found " + str(close_count) + "\nGetting merged count", end='')
        merged_count = call_github(merged_url)
        if verbose:
            print(" Found " + str(merged_count) + "\nGetting draft count", end='')
        draft_count = call_github(draft_url)
        if verbose:
            print(" Found " + str(draft_count) + "\nGetting total open count", end='')
        total_open_count = call_github(total_open_url)
        if verbose:
            print(" Found " + str(total_open_count) + "\nGetting total closed count", end='')
        total_close_count = call_github(total_close_url)
        if verbose:
            print(" Found " + str(total_close_count) + "\nGetting first respose metrics", end='')
        first_response = call_first_response(first_response_url)
        if verbose:
            print("Found " + str(first_response['with_comments']) + " with comments, " + str(first_response['without_comments']) + " without comments, " + str(first_response['self_merge']) + " self merge no comments, " + str(first_response['uncounted']) + " self closed no comments.")

        if first_response['with_comments']:
            average_response = round(first_response['total_days'] / first_response['with_comments'], 1)
        else:
            average_response = "NULL"
        f.write('{},{},{},{},{},{},{},{},{},{},{},{}\n'.format(end_date, open_count, draft_count, close_count - merged_count, merged_count, total_open_count, total_open_count - total_close_count, average_response, first_response['with_comments'], first_response['without_comments'], first_response['self_merge'], first_response['uncounted']))
        current_date = current_date + datetime.timedelta(days=7)
        if not verbose:
            print("Done!")
    f.close()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
                    prog='get_prs',
                    description='Gets the pull request counters for MariaDB Server')
    parser.add_argument('start_wn', help='Start week number (for example 2022-W04)')
    parser.add_argument('end_wn', help='End week number (for example 2023-W06)')
    parser.add_argument('-v', '--verbose', action=argparse.BooleanOptionalAction)
    args = parser.parse_args()
    verbose = args.verbose
    generate(args.start_wn, args.end_wn)

