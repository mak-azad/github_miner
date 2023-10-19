import subprocess
import shutil
import os
import pandas as pd
import asyncio

# Function to check if a command is available in the system
def is_command_available(command):
    return shutil.which(command) is not None

# Function to install pssh if not already installed
def install_pssh():
    if not is_command_available("pssh"):
        print("Parallel SSH (pssh) is not installed. Installing...")
        subprocess.run(["pip", "install", "pssh"])

# Function to read SSH hosts from a file
def read_ssh_hosts(filename):
    with open(filename, "r") as hosts_file:
        return [line.strip() for line in hosts_file]

# Function to remove the first row (header) from a CSV file
def remove_csv_header(input_csv):
    input_df = pd.read_csv(input_csv)
    input_df = input_df.iloc[1:]  # Remove the first row (header)
    return input_df

# Function to split data into separate input CSV files for each node
def split_csv_data(input_df, num_nodes, hostnames):
    rows_per_node = len(input_df) // num_nodes
    split_data = []
    for i in range(num_nodes):
        start_row = i * rows_per_node
        end_row = start_row + rows_per_node
        node_df = input_df[start_row:end_row]

        # Append the IP address to the filename
        filename = f"github_repositories_{hostnames[i]}.csv"
        node_df.to_csv(filename, index=False)
        split_data.append(filename)
    return split_data

# Function to copy files to remote nodes using pscp
def copy_files_to_nodes(files_to_copy, ssh_hosts, data_to_copy):
    for i, host in enumerate(ssh_hosts):
        for file in files_to_copy:
            print(f"Copying {file} and {data_to_copy[i]} to {host}...")
            subprocess.run(["pscp", file, f"{host}:/path/to/destination/"])
            subprocess.run(["pscp", data_to_copy[i], f"{host}:/path/to/destination/"])
            print(f"{file} and {data_to_copy[i]} copied to {host}")

# Function to execute commands on a single node
async def execute_commands_on_node(host, commands):
    for command in commands:
        print(f"Executing '{command}' on {host}...")
        subprocess.run(["pssh", "-h", host, command])
        print(f"Command '{command}' executed on {host}")

# Function to execute commands on remote nodes asynchronously
async def execute_commands_on_nodes(ssh_hosts, commands):
    tasks = []
    for host in ssh_hosts:
        task = execute_commands_on_node(host, commands)
        tasks.append(task)
    await asyncio.gather(*tasks)

# Main function to execute the entire script
def main():
    install_pssh()

    files_to_copy = ["authenticator.sh", "repo_analyzer.py"]
    ssh_hosts = read_ssh_hosts("sshhosts")

    input_csv = "github_repositories.csv"
    input_df = remove_csv_header(input_csv)

    num_nodes = len(ssh_hosts)
    hostnames = ssh_hosts
    split_data = split_csv_data(input_df, num_nodes, hostnames)

    copy_files_to_nodes(files_to_copy, ssh_hosts, split_data)

    commands = [
        "sh /path/to/destination/authenticator.sh",
        "python /path/to/destination/repo_analyzer.py /path/to/destination/github_repositories_{{host}}.csv"
    ]

    for i, host in enumerate(ssh_hosts):
        commands[i] = commands[i].replace("{{host}}", host)

    asyncio.run(execute_commands_on_nodes(ssh_hosts, commands))

    print("File copy and command execution on remote nodes completed.")

if __name__ == "__main__":
    main()
