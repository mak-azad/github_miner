# Github Miner
A tool to search github repositories and process information found from each of the repositories

## Pre-requisites
Python `3.8+`

## 1. Fetch github repositories and export in a CSV file
Use the following command to fetch repositories from github and export into the file `github_repositories.csv`
```
python repo_fetcher.py --language <LANGUAGE> --stars <MINIMUM_STARS> --forks <MINIMUM_FORKS> --last_commit <LAST_UPDATE_DATE> --result_limit <NUMBER_OF_REPO>
```

For example see the command below
```
python repo_fetcher.py --language Python --stars 100 --forks 10 --last_commit 2023-01-01 --result_limit 2000
```

You can run without any filter as the command below, then the script applies the above filters by default<br>
`python repo_fetcher.py`

## 2. Run the commit analyzer on multi-node cluster using parallel ssh
### Create the hosts file
Add all the node ip addresses line by line into the `sshhosts` file

### Ensure inter-node ssh permissions
Execute the authenticator scripts inside each nodes at first<br>
Run command: `sh authenticator.sh`

### Execute the analyzer on multiple nodes in parallel
Run the following command to execute the analyzer using parallel-ssh
```
parallel-ssh -A -i -h sshhosts python repo_analyzer.py
```