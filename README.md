# MariaDB Metrics Tools

This is a repository containing tools used to generate metrics on the MariaDB code and community. This is designed to be easily observed and contributed to by the MariaDB Community.

## pull-requests

In this directory there is a Python script to use the GitHub API to scrape metrics about the MariaDB server pull requests and generate a CSV output. It uses the "issues" API to gather counts in the response rather than getting whole responses so that the amount of API requests required can be reduced. It also deliberately waits 2 seconds between requests so that GitHub's rate limit is not hit.

## commits

This directory contains a shell script to cache a git log and pipe it into a tool called "gitdm" which processes the commit history to generate metrics. There are a set of files in here which map contributors to their affiliations, both on a domain basis and on an individual basis when their email domain cannot determine this.

## We need your help!

If you are a contributor to MariaDB it would help us immensely if you could look at the files in [`commits/config/`](commits/config/) to check that any details about your affiliation are correct. Details on these files can be found in the commits directory [README.md](commits/README.md).
