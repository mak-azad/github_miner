import subprocess
import shutil
import os
import pandas as pd
import asyncio

# Function to check if a command is available in the system
def is_command_available(command):
    return shutil.which(command) is not None

# Function to read SSH hosts from a file
def read_ssh_hosts(filename):
    with open(filename, "r") as hosts_file:
        return [line.strip() for line in hosts_file]

# Function to split data into separate input CSV files for each node
def split_csv_data(input_csv, num_nodes, hostnames, split_files_dir):
    input_df = pd.read_csv(input_csv)
    rows_per_node = len(input_df) // num_nodes
    split_data = []
    for i in range(num_nodes):
        start_row = i * rows_per_node
        end_row = start_row + rows_per_node
        node_df = input_df[start_row:end_row]

        # Append the IP address to the filename
        filename = os.path.join(split_files_dir, f"github_repositories_{hostnames[i]}.csv")
        node_df.to_csv(filename, index=False)
        split_data.append(filename)
    return split_data

# Function to copy files to remote nodes using parallel-scp
def copy_files_to_nodes(files_to_copy, ssh_hosts, data_to_copy, destination_path, user):
    for i, host in enumerate(ssh_hosts):
        remote = user + "@" + host + ":" + destination_path
        for file in files_to_copy:
            print(f"Copying {file} to {host}...")
            subprocess.run(["scp", file, remote])
        print(f"Files copied to {host}")
        print(f"Copying {data_to_copy[i]} to {host}...")
        subprocess.run(["scp", data_to_copy[i], remote])
        print(f"{data_to_copy[i]} copied to {host}")

# Function to execute commands on a single node using parallel-ssh
async def execute_commands_on_node(host, commands):
    for command in commands:
        print(f"Executing '{command}' on {host}...")
        subprocess.run(["parallel-ssh", "-r", "-h", host, command])
        print(f"Command '{command}' executed on {host}")

# Function to execute commands on remote nodes using parallel-ssh
async def execute_commands_on_nodes(ssh_hosts, commands):
    tasks = []
    for host in ssh_hosts:
        task = execute_commands_on_node(host, commands)
        tasks.append(task)
    await asyncio.gather(*tasks)

# Main function to execute the entire script
def main():
    user = "ssmtariq"
    split_files_dir = "analyzer"  # Set output directory for the split files
    files_to_copy = [f"{split_files_dir}/repo_analyzer.py", f"{split_files_dir}/pygitclient.py"]
    ssh_hosts = read_ssh_hosts("sshhosts")

    input_csv = "github_repositories.csv"  # Ensure the header is present
    num_nodes = len(ssh_hosts)
    hostnames = ssh_hosts
    split_data = split_csv_data(input_csv, num_nodes, hostnames, split_files_dir)

    destination_path = f"/users/ssmtariq/github_miner/{split_files_dir}"  # Set your destination path here

    copy_files_to_nodes(files_to_copy, ssh_hosts, split_data, destination_path, user)

    commands = [
        f"python {destination_path}repo_analyzer.py {destination_path}github_repositories_{{host}}.csv"
    ]

    # for i, host in enumerate(ssh_hosts):
    #     commands[i] = commands[i].replace("{{host}}", host)

    # asyncio.run(execute_commands_on_nodes(ssh_hosts, commands))

    print("File split and copy on remote nodes completed.")

if __name__ == "__main__":
    main()
