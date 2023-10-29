import pygit2
import socket
import os

# Set Git Credentials
username = 'ssmtariq'
token = ''  # You can use a Personal Access Token (PAT) as well
email = 'syedtariqfiles@gmail.com'
host_ip = socket.gethostbyname(socket.gethostname())

def commit_n_push():

    output_csv_file = os.path.join(f"analyzer/results", f"github_repo_analysis_result_{host_ip}.csv")

    if os.path.exists(f'/users/{username}/github_miner/'+output_csv_file):
        repository_path = f'/users/{username}/github_miner'
        remote_name = 'origin'
        branch_name = 'main'

        repo = pygit2.Repository(repository_path)
        remote = repo.remotes[remote_name]
        print("Remote name: ", remote)

        if fetch_remote_changes(remote):
            if has_changes_to_commit(repo, output_csv_file):
                commit_and_push(repo, output_csv_file, username, email, branch_name)
                print("Changes committed and pushed successfully.")
            else:
                print("No changes to commit.")
        else:
            print("Failed to fetch remote changes.")
    else:
        print(f"The file {output_csv_file} does not exist. Skipping commit and push.")

def fetch_remote_changes(remote):
    try:
        remote.fetch()
        return True
    except Exception as e:
        print(f"Failed to fetch remote changes: {e}")
        return False

def has_changes_to_commit(repo, output_csv_file):
    index = repo.index
    print("Index found: ", index)

    # Check if the file is in the index (staged for commit)
    for entry in index:
        if entry.path == output_csv_file:
            return True

    # If the file is not in the index, stage it for commit
    if os.path.exists(output_csv_file):
        print("The file inside has_changes_to_commit() exists: ", output_csv_file)
    index.add(output_csv_file)
    index.write()
    return True

def commit_and_push(repo, output_csv_file, username, email, branch_name):
    index = repo.index
    index.add(output_csv_file)
    index.write()
    tree = index.write_tree()
    author = pygit2.Signature(username, email)
    committer = author
    message = "Update result file from the host: " + host_ip
    commit_oid = repo.create_commit('HEAD', author, committer, message, tree, [repo.head.target])
    credentials = pygit2.UserPass(username, token)
    repo.remotes['origin'].push(["refs/heads/" + branch_name], callbacks=pygit2.RemoteCallbacks(credentials=credentials))