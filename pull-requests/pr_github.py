import os
import sys
import time
import requests
import json
import re

GITHUB_TOKEN = os.environ['GITHUB_TOKEN']

auth_header = {'Authorization': 'token ' + GITHUB_TOKEN}


def get_data(url, verbose):
    response = requests.get(url, headers = auth_header)
    if response.status_code != 200:
        print("Failed to get json data: " + str(response.headers))
        exit()
    if (int(response.headers['X-RateLimit-Remaining']) <= 2):
        if verbose:
            print("\nRate limit low, remaining " + response.headers['X-RateLimit-Remaining'] + " sleeping for 30 seconds", end='')
        else:
            print('_', end='')
        time.sleep(30)
    else:
        print('.', end='')
    sys.stdout.flush()

    return response

def get_paginated_data(url, verbose):
    data = []
    while(True):
        response = get_data(url, verbose)
        data.append(json.loads(response.text))
        try:
            groups = re.search(r"<([^<]*)>; rel=\"next\"", response.headers['Link'])
            url = groups.group(1)
        except:
            break
    return data

def get_json_data(url, verbose):
    response = get_data(url, verbose)
    return json.loads(response.text)

