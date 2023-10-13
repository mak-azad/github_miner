from pydriller import Repository
import csv

def read_repository_urls_from_csv(input_csv_file):
    with open(input_csv_file, 'r') as input_file:
        reader = csv.reader(input_file)
        repo_urls = [row[0] for row in reader]
    return repo_urls

def analyze_repository(repo_url):
    commit_data = []
    for commit in Repository(repo_url).traverse_commits():
        commit_data.append([commit.hash, commit.msg, commit.author.name])
    return commit_data

def write_commit_analysis_to_csv(output_csv_file, commit_data):
    with open(output_csv_file, 'w', newline='') as output_file:
        writer = csv.writer(output_file)
        # Write the header row
        writer.writerow(["Commit Hash", "Message", "Author Name"])
        # Write the commit data
        writer.writerows(commit_data)

def main():
    input_csv_file = "repository_urls.csv"
    output_csv_file = "commit_analysis_result.csv"

    # Read repository URLs from the input CSV
    repo_urls = read_repository_urls_from_csv(input_csv_file)

    all_commit_data = []
    for repo_url in repo_urls:
        # Analyze each repository and collect commit data
        commit_data = analyze_repository(repo_url)
        all_commit_data.extend(commit_data)
    # Write all commit analysis data to the output CSV
    write_commit_analysis_to_csv(output_csv_file, all_commit_data)

if __name__ == "__main__":
    main()
