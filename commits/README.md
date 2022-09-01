# Commit Metrics

We are using GitDM to process the git tree for MariaDB and generate metrics based on individuals and their affiliations. It pulls and process everything on the MariaDB tree so that commits to older branches (bug fixes) are counted.

You can execute this by running `./get_git_log.sh <START_DATE> <END_DATE>`. This will generate a text file and two CSV files for the given date range.

You can also call `./generate_3+year.sh` which will generate the last 3 years and this year. It will then put the people CSV files into `people.csv` with an additional column for "Year".

GitDM is configured using the files in the `gitdm_config` subdirectory. The key files here help determine which company a given individual email address works for, and alises between addresses. The files are as follows:

## domain-map

This is a catchall for an email domain name to company mapping.

## aliases

This contains a list of email addresses which are aliases to other email addresses.

## employers

This contains a list of email addresses which do not fit into the above categories, such as personal email addresses or individuals, to determine a given contributor's affiliation.
