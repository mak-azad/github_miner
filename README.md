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

### Check if all worker nodes are accessible from the master node
Run the following command to using parallel-ssh to print the node names. Do not run any further `parallel` commands until this one executes sucessfully.
```
parallel-ssh -i -h sshhosts -O StrictHostKeyChecking=no hostname
```

### Clone the github_miner repository in all nodes to upload the commit analysis results
```
parallel-ssh -i -h sshhosts 'git clone https://github.com/ssmtariq/github_miner.git'
```

### Configure the Python Git client with your Git username, email and token. 
Open the file `analyzer/pygitclient.py` and set values for the variables username, token and email

### Run script to split and distribute the input files along with analyzer among the nodes
```
python3.8 task_parallelizer.py
```

### Rename the splitted input csv file to run using parallel-ssh command
```
parallel-ssh -i -h sshhosts 'find . -type f -name "github_miner/analyzer/github*.csv" -exec mv {} github_miner/analyzer/input.csv \;'
```

### Execute the analyzer on multiple nodes in parallel
Run the following command to execute the analyzer using parallel-ssh
```
parallel-ssh -A -i -h sshhosts python github_miner/analyzer/repo_analyzer.py
```