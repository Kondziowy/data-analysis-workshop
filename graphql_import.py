import requests

# Define the GraphQL query
query = '''
    query {
        systemMetrics {
            cpuPercent
            memoryUsage
            diskUsage
        }
    }
'''

# Set the URL of the GraphQL endpoint
url = 'http://localhost:8000/graphql'

# Set the headers for the request
headers = {
    'Content-Type': 'application/json',
}

# Set the request payload
payload = {
    'query': query,
}

# Make the GraphQL request
response = requests.post(url, json=payload, headers=headers)

# Load the JSON response data into a Python dictionary
data = response.json()['data']['systemMetrics']

# Print the data
print(data)