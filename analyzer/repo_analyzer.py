import socket
from pydriller import Repository
# from pygitclient import commit_n_push
import csv
import os

file_type = '.py'
published_commits = 0
commit_counter = 0
# Set number of commits after which result file will be pushed to github
buffer_size = 100

# Create a 'results' directory if it doesn't exist
results_dir = 'results'
if not os.path.exists(results_dir):
    os.mkdir(results_dir)

def read_repository_urls_from_csv(input_csv_file):
    with open(input_csv_file, 'r') as input_file:
        reader = csv.reader(input_file)
        repo_urls = [row[0] for row in reader]
    return repo_urls

def analyze_repository(repo_url, output_csv_file):
    global commit_counter
    global published_commits
    commit_data = []
    for commit in Repository(repo_url, only_modifications_with_file_types=[file_type]).traverse_commits():
        commit_data.append([commit.project_name, commit.hash, commit.msg, commit.insertions, commit.deletions, commit.committer_date, commit.lines, commit.files, commit.author.name])
        commit_counter += 1

        #Push interim commit analysis result to github
        if commit_counter % buffer_size == 0:
            published_commits +=buffer_size
            write_commit_analysis_to_csv(output_csv_file, commit_data)
            # commit_n_push()
            print(f"{commit_counter} commits are added")

    return commit_data

def write_commit_analysis_to_csv(output_csv_file, commit_data):
    with open(output_csv_file, 'a', newline='') as output_file:
        writer = csv.writer(output_file)
        if output_file.tell() == 0:
            # If the file is empty, write the header row
            writer.writerow(["Project Name", "Commit Hash", "Message", "Additions", "Deletions", "Commit Date", "Lines changed", "Files Changed", "Author Name"])
        # Write the commit data
        writer.writerows(commit_data)

def main():

    # Generate the output file name with the specified prefix and IP address
    host_ip = socket.gethostbyname(socket.gethostname())
    # Define the input CSV file name
    input_csv_file = f"github_repositories_{host_ip}.csv"
    repo_urls = read_repository_urls_from_csv(input_csv_file)
    # Specify the output file path inside the 'results' directory
    output_csv_file = os.path.join(results_dir, f"github_repo_analysis_result_{host_ip}.csv")

    all_commit_data = []
    for repo_url in repo_urls:
        # Analyze each repository and collect commit data
        commit_data = analyze_repository(repo_url)
        all_commit_data.extend(commit_data)

    # Write any remaining commit analysis data to the output CSV
    if all_commit_data:
        write_commit_analysis_to_csv(output_csv_file, all_commit_data)
        # commit_n_push()

if __name__ == "__main__":
    main()
# if commit_counter>published_commits: