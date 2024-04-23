## Pull Request Metrics

### get_prs.py

This tool gets the PR counts for 2022 and stores them in `prs-<START>..<END>.csv`. There is rate-limit handling built in because some calls are only allowed to do 30 requests per minute. It will also pause and retry upon 500 server errors.

To execute this you will need a GitHub token from https://github.com/settings/tokens/new and set this as the environment variable `GITHUB_TOKEN`. You need to provide a date range using week numbers. For example, to generate a 2022 report:

```
./get_prs.py 2022-W1 2022-W52
```

You can also add `-v` to the command line parameters to verbosely output the progress

### report.py

This generates a list of pull requets that require attention. Options are:

* `-r` - report type, `old` gets the pull requests sorted by oldest first, `new` gets the pull requests sorted by newest first. This is a required parameter.
* `-d` - days, the minimum number of days since last action to add the PR to the report. Default is `7`.
* `-l` - limit, the maxiumu number of items to add to the final output report. Default is `30`. `0` means unlimited.
* `-s` - sort order, `longest` sorts the final output by the longest time since the last response, `shortest` sorts by the shortest time since the last response. By default it will be unsorted, so ordered by the report type option.
* `-v` - verbose, add verbose output to the console.

As with `get_prs.py`, you will require the `GITHUB_TOKEN` environment variable.

### plot_prs.py

This plots the new open/closed statuses for each week, using data from a CSV file. It requires `matplotlib` and `numpy` Python packages are installed (both in standard distro packages and PyPi). It requires you to provied the CSV file as a parameter and generates the file `prs.png` as an output. As an example you would execute it using:

```
./plot_prs.py prs-2022-W1..2022-W52.csv
```

### plot_totals.py

This plots the total count of open/closed PRs for each week using the data from a CSV file. It also requires `matplotlib` and `numpy` Python packages. It requires you to provied the CSV file as a parameter and generates the file `prs_total.png` as an output. As an example you would execute it using:

```
./plot_totals.py prs-2022-W1..2022-W52.csv
```

