import pygit2
import socket

# Set Git Credentials
username = 'ssmtariq'
token = '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'  # You can use a Personal Access Token (PAT) as well
email = 'syedtariqfiles@gmail.com'

def commit_n_push():

    # Generate the output file name with the specified prefix and IP address
    host_ip = socket.gethostbyname(socket.gethostname())
    output_csv_file = f"github_repo_analysis_result_{host_ip}.csv"

    # Replace these values with your repository information
    repository_path = f'/users/{username}/github_miner'
    remote_name = 'origin'
    branch_name = 'main'  # Replace with your branch name

    # Open the repository
    repo = pygit2.Repository(repository_path)

    # Get the remote
    remote = repo.remotes[remote_name]

    # Fetch the latest changes from the remote
    remote.fetch()

    # Get the status of the repository
    status = repo.status()
    # Check if there are changes to commit
    if output_csv_file in status and status[output_csv_file] != pygit2.GIT_STATUS_CURRENT:
        # Create a new commit with a message
        index = repo.index
        index.add(output_csv_file)  # Only add the specific file
        index.write()
        tree = index.write_tree()
        author = pygit2.Signature(username, email)
        committer = author
        message = "Update result file from the host: "+host_ip
        commit_oid = repo.create_commit('HEAD', author, committer, message, tree, [repo.head.target])

        # Push the commit to the remote branch
        credentials = pygit2.UserPass(username, token)
        remote.push(["refs/heads/" + branch_name], callbacks=pygit2.RemoteCallbacks(credentials=credentials))

        print("Changes committed and pushed successfully.")
    else:
        print("No changes to commit.")