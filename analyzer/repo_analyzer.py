import socket
from pydriller import Repository
from pydriller import Commit
from pygitclient import commit_n_push
import csv
import os
import argparse

root_dir = "github_miner/analyzer"
file_type = '.py'
published_commits = 0
commit_counter = 0
# Set the number of commits after which the result file will be pushed to GitHub
buffer_size = 100

general_keywords = ["deadlock", "race condition", "synchronization error", "mutex", "semaphore", "starvation", "locking", 
                    "multiple", "concurrency", "concurrent", "parallel", "multithreading", "threading", "threads", "thread pool", 
                    "multiprocessing", "await", "async", "atomic", "asyncio", "concurrent.futures"]
concurrency_keywords = ["await", "awaitable" "async", "asyncio", "create_task", "semaphore", "threading", "multiprocessing", "concurrent.futures"]

# Create a 'results' directory if it doesn't exist
results_dir = f'{root_dir}/results'
if not os.path.exists(results_dir):
    os.mkdir(results_dir)

def read_repository_urls_from_csv(input_csv_file):
    print("Processing input filename: ", input_csv_file)
    with open(input_csv_file, 'r') as input_file:
        reader = csv.reader(input_file)
        # Skip the header row
        next(reader, None)
        repo_urls = [row[6] for row in reader]
    return repo_urls

def filter_commit(commit):
    # Check if the commit message contains any keywords from general_keywords
    if any(keyword in commit.msg for keyword in general_keywords):
        modified_files = []

        # Iterate through the modified files in the commit
        for file in commit.modified_files:
            # Get the diff of each file
            diff = file.diff

            # Look for added lines in the diff
            added_lines = [
                line
                for line in diff.split("\n")
                if line.startswith("+") and not line.startswith("+++")
            ]

            # Check if any added line contains keywords from concurrency_keywords
            if any(
                keyword in line
                for line in added_lines
                for keyword in concurrency_keywords
            ):
                modified_files.append(file)

        # Create a new Commit object with the filtered files
        filtered_commit = Commit(
            commit.hash,
            commit.author.name,
            commit.author.email,
            commit.msg,
            commit.author_date,
            commit.committer_date,
            modified_files,
            commit.parents,
        )

        return filtered_commit

    return None

def analyze_repository(repo_url, output_csv_file):
    global commit_counter
    global published_commits
    commit_data = []
    for commit in Repository(repo_url, only_modifications_with_file_types=[file_type]).traverse_commits():
        filtered_commit = filter_commit(commit)
        if filtered_commit is not None:
            commit = filtered_commit
            original_codes = []
            modified_codes = []
            modified_files = []
            methods_before = []
            methods_after = []
            for m in commit.modified_files:
                try:
                    original_codes.append(m.source_code_before)
                    modified_codes.append(m.source_code)
                    modified_files.append(m.filename)
                    methods_before.append(m.methods_before)
                    methods_after.append(m.changed_methods)
                except ValueError as e:
                    print(f"Error processing commit {commit.hash}: {e}")
                    continue  # Continue with the next commit if an error occurs

            commit_data.append([commit.project_name, commit.hash, commit.msg, commit.committer_date, commit.author.name, commit.insertions, 
                                commit.deletions, commit.lines, commit.files, modified_files, original_codes, modified_codes, methods_before, methods_after])
            commit_counter += 1
            # Push interim commit analysis result to GitHub
            if commit_counter % buffer_size == 0:
                published_commits += buffer_size
                write_commit_analysis_to_csv(output_csv_file, commit_data)
                print(f"{commit_counter} commits are added")
    # Ensure all commits are written to result file
    if(commit_counter>published_commits):
        write_commit_analysis_to_csv(output_csv_file, commit_data)
    return commit_data

def roll_output_csv_file(output_csv_file, counter):
    # Incrementally name the new file
    filename_parts = os.path.splitext(output_csv_file)
    new_output_csv_file = f"{filename_parts[0]}_{counter}.csv"
    os.rename(output_csv_file, new_output_csv_file)

def write_commit_analysis_to_csv(output_csv_file, commit_data):
    with open(output_csv_file, 'a', newline='') as output_file:
        writer = csv.writer(output_file)
        if output_file.tell() == 0:
            # If the file is empty, write the header row
            writer.writerow(["Project Name", "Commit Hash", "Message", "Commit Date", "Author Name", "Additions", "Deletions", "Lines changed", "Files Changed", "Modified files", "Original Code", "Modified Code", "Methods Before", "Methods After"])
        # Write the commit data
        writer.writerows(commit_data)

def main():

    # Generate the output file name with the specified prefix and IP address
    host_ip = socket.gethostbyname(socket.gethostname())
    # Define the input CSV file name
    input_csv_file = os.path.join(root_dir, f"github_repositories_{host_ip}.csv")
    repo_urls = read_repository_urls_from_csv(input_csv_file)
    # Specify the output file path inside the 'results' directory
    output_csv_file = os.path.join(results_dir, f"github_repo_analysis_result_{host_ip}.csv")

    for repo_url in repo_urls:
        # Analyze each repository and collect commit data
        print("Processing repo url: ", repo_url)
        analyze_repository(repo_url, output_csv_file)

    # Push all the changes in the analyzer/results directory to github
    # commit_n_push(username=args.username, token=args.token, email=args.email)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="GitHub Miner Analyzer")
    parser.add_argument("--username", required=True, help="Git username")
    parser.add_argument("--token", required=True, help="Git token")
    parser.add_argument("--email", required=True, help="Git email")
    args = parser.parse_args()
    main()