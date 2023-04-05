import requests

# First, set up the necessary headers and authentication details
ACCESS_TOKEN = "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"
headers = {"Authorization": f"Bearer {ACCESS_TOKEN}", "Accept": "application/vnd.github.v3+json"}

# Next, specify the repository owner and name
owner = "Kondziowy"
repo_name = "llama-bot"

# Then, make a request to get the actions workflow runs for the repository
url = f"https://api.github.com/repos/{owner}/{repo_name}/actions/runs"
response = requests.get(url, headers=headers)

# Check if the request was successful
if response.status_code != 200:
    print("Error: Request failed with status code", response.status_code)
    exit()

# Parse the response JSON and print out the ID and status of each run
runs = response.json()["workflow_runs"]
# Take head commit + id
# List files changed per commit
for run in runs:
    print(f"Run ID: {run['id']}, Status: {run['status']}, Created at: {run['created_at']}, Pull requests: {run['pull_requests']}")