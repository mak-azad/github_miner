# github_miner
A tool to search github repositories and process information found from each of the repositories

## Pre-reuisites
Python `3.8+`

### Fetch github repositories and export in a CSV file
Use the following command to fetch repositories from github and export into the file "github_repositories.csv"
`python repo_fetcher.py --language <LANGUAGE> --stars <MINIMUM_STARS> --forks <MINIMUM_FORKS> --last_commit <LAST_UPDATE_DATE> --result_limit <NUMBER_OF_REPO>`<br>
For example see the command below<br>
`python repo_fetcher.py --language Python --stars 100 --forks 10 --last_commit 2023-01-01 --result_limit 2000`<br>
You can run without any filter as the command below, then the script applies the above filters by default<br>
`python repo_fetcher.py`
