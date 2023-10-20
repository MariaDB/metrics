# MariaDB READMEs Metrics

## github_readmes_mysql_no_mariadb.py

Python sript that searches READMEs in github repos that mention MySQL, but not MariaDB. The output csv can be used as a starting point for evaluating if repositories should also mention MariaDB.

Repos are prioritized and filterd based on amount of stars (as an indicator of popularity). Inactive repos are filterd out if they haven't has a push within a year. Repos with stars less than STARS_THRESHOLD are filtered out, the default value being 5000 which can be changed in the code. 

Statistics based on STARS_THRESHOLD: 
* with 5000 stars or more, there are 287 repositories with MySQL but not MariaDB in the README (16th October 2023)
* with 1000 stars or more, there are 1271 repos (16th October 2023)
* with 0 or more stars, there are 428 786 repos (16th October 2023)

The script can be run without a Github API-token. The code required to include an API token in the API requests is present, but has been commented out using a '#' symbol.