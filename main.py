import os
import requests
from requests.auth import HTTPBasicAuth
from jinja2 import Environment, FileSystemLoader

hostname = os.getenv("ELASTIC_HOSTNAME")
verify = os.getenv("SSL_IGNORE_CERTIFICATE", 'True').lower() not in ('true', '1', 't')
port = os.getenv("ELASTIC_PORT")

username = os.getenv("ELASTIC_USERNAME")
password = os.getenv("ELASTIC_PASSWORD")

index_name = os.getenv("INDEX_NAME")

templates_path = os.getenv("TEMPLATES_PATH")

auth = HTTPBasicAuth(username, password)
headers = {
    "Content-Type": "application/json"
}

url = f"https://{hostname}:{port}"
base_url = url

# test
resp = requests.get(url, auth=auth, headers=headers, verify=verify)
assert resp.status_code == 200

env = Environment(loader=FileSystemLoader(templates_path))
mapping_template = env.get_template("mapping.txt")
doc_template = env.get_template("doc.txt")

field_types = [
    "integer",
    "double"
]

field_values = [
    1,
    2.3
]

for i, field_type in enumerate(field_types):
    for j, field_value in enumerate(field_values):
        if i == j:
            continue
        
        # NOTE: delete index
        url = f"{base_url}/{index_name}"
        resp = requests.delete(url, auth=auth, headers=headers, verify=verify)
        # assert resp.status_code == 200
        
        # NOTE: create index
        body = mapping_template.render(
            field_type=field_type
        )

        url = f"{base_url}/{index_name}"
        resp = requests.put(url, auth=auth, headers=headers, verify=verify, data=body)
        assert resp.status_code == 200

        # NOTE: add doc
        body = doc_template.render(
            field_value=field_value
        )
        url = f"{base_url}/{index_name}/_doc/1"
        resp = requests.put(url, auth=auth, headers=headers, verify=verify, data=body)
        assert resp.status_code == 201


