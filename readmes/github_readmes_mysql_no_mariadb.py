import requests
import time
import pandas as pd
from datetime import datetime, timedelta
import os
import logging

ONLY_COUNT = False
STARS_THRESHOLD = 5000
OUTPUT_PATH = "" # where to output csv
#API_TOKEN_PATH = ".apitoken" # text file with only Github API-token

#def get_api_token():
#    with open(API_TOKEN_PATH, "r") as apitokenfile:
#        return apitokenfile.read()

def search_readmes(query, only_count=ONLY_COUNT):
    logging.info(f"Query: {query}")
    url = "https://api.github.com/search/repositories"
    headers = {
        #"Authorization": f"Bearer {get_api_token()}",
        "Accept": "application/vnd.github.v3+json"
    }
    params = {
        "q": query,
        "per_page": 100,
        "page": 1
    }
    i = 0
    j = 0
    results = []
    while True:
        try:
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()  # Raise an exception for non-2xx responses
            data = response.json()
            i = i+1
            total_count = data["total_count"]
            if i==1:
                logging.info("Total Count of Repositories: %d", total_count)
            if only_count:
                break
            for item in data["items"]:
                j = j+1
                logging.info("page %d, %d/%d, %s, %s", i, j, total_count, item['name'], item['html_url'])
                results.append({'name':item['name'], 'stars':item['stargazers_count'], 'url':item['html_url'], 'item':item})
            if "next" in response.links:
                next_url = response.links["next"]["url"]
                params["page"] += 1
                time.sleep(1)
            else:
                break
        except requests.exceptions.RequestException as e:
            logging.error("Error while making the request: %s", str(e))
            break

    if not only_count:
        logging.info("Gathered %d results out of %d.", len(results), total_count)
        # csv output
        df = pd.DataFrame(results)
        df = df.sort_values(by='stars', ascending=False)
        output_csv_file = os.path.join(OUTPUT_PATH, "github_readmes_mysql_no_mariadb.csv")
        df.to_csv(output_csv_file,index=False)
        logging.info("Saved to %s", output_csv_file)

def main():
    one_year_ago_str = (datetime.now() - timedelta(days=365)).strftime("%Y-%m-%dT%H:%M:%SZ")
    query_mysql_no_mariadb = f"mysql in:readme stars:>={STARS_THRESHOLD} NOT mariadb pushed:>{one_year_ago_str}"
    search_readmes(query_mysql_no_mariadb, only_count=ONLY_COUNT)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()