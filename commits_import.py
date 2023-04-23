import requests
import json

ACCESS_TOKEN = "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"
headers = {"Authorization": f"Bearer {ACCESS_TOKEN}", "Accept": "application/vnd.github.v3+json"}


# Next, specify the repository owner and name, and the branch you're interested in
owner = "Kondziowy"
repo_name = "llama-bot"
branch = "main"

# Then, make a request to get the commits for the specified branch
url = f"https://api.github.com/repos/{owner}/{repo_name}/commits?sha={branch}"
response = requests.get(url, headers=headers)

# Check if the request was successful
if response.status_code != 200:
    print("Error: Request failed with status code", response.status_code)
    exit()

# Parse the response JSON and print out the commit SHA and message for each commit
commits = response.json()
for commit in commits:
    print(f"Commit SHA: {commit['sha']}, Message: {commit['commit']['message']}, Date: {commit['commit']['author']['date']}")


with open("data/github-output.json", "w") as f:
    json.dump(commits, f)