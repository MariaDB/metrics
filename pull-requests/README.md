## Pull Request Metrics

### get_prs.py

This tool gets the PR counts for 2022 and stores them in `prs-<START>..<END<.csv`. There is a deliberate 2 second pause between each request so as not to hit the GitHub rate limit (30 requests per minute).

To execute this you will need a GitHub token from https://github.com/settings/tokens/new and set this as the environment variable `GITHUB_TOKEN`. You need to provide a date range using week numbers. For example, to generate a 2022 report:

```
./get_prs.py 2022-W1 2022-W52
```

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
