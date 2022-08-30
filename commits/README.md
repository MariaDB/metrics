# Commit Metrics

We are using GitDM to process the git tree for MariaDB and generate metrics based on individuals and their affiliations. It pulls and process everything on the MariaDB tree so that commits to older branches (bug fixes) are counted.

GitDM is configured using the files in the `gitdm_config` subdirectory. The key files here help determine which company a given individual email address works for, and alises between addresses. The files are as follows:

## domain-map

This is a catchall for an email domain name to company mapping.

## aliases

This contains a list of email addresses which are aliases to other email addresses.

## employers

This contains a list of email addresses which do not fit into the above categories, such as personal email addresses or individuals, to determine a given contributor's affiliation.
