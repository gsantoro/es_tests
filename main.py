import os
import requests
from requests.auth import HTTPBasicAuth

hostname = os.getenv("ELASTIC_HOSTNAME")
verify = os.getenv("SSL_IGNORE_CERTIFICATE", 'True').lower() not in ('true', '1', 't')
port = os.getenv("ELASTIC_PORT")
username = os.getenv("ELASTIC_USERNAME")
password = os.getenv("ELASTIC_PASSWORD")

url = f"https://{hostname}:{port}"
auth = HTTPBasicAuth(username, password)
headers = {
    "Content-Type": "application/json"
}

resp = requests.get(url, auth=auth, headers=headers, verify=verify)
print(f"request: {resp.request}")
print(f"response: {resp}")