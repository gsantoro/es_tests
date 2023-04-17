import json
import os
import requests
from requests.auth import HTTPBasicAuth
from jinja2 import Environment, FileSystemLoader, select_autoescape
import structlog
from jsonpath_ng.ext import parse
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

log = structlog.get_logger()

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
assert resp.status_code == 200, "connection refused"

env = Environment(
    loader=FileSystemLoader(templates_path), 
    autoescape=select_autoescape(default_for_string=True, default=False))
mapping_template = env.get_template("mapping.txt")
doc_template = env.get_template("doc.txt")

field_types = [
    "integer",
    "double",
    "ip"
]

field_values = [
    1,
    2.3,
    "\"192.168.1.1\""
]

for i, field_type in enumerate(field_types):
    for j, field_value in enumerate(field_values):
        if i == j:
            continue
        
        log.info("Trying indexing...", field_type=field_type, field_value=field_value)
        
        # NOTE: delete index
        url = f"{base_url}/{index_name}"
        resp = requests.delete(url, auth=auth, headers=headers, verify=verify)
        if resp.status_code >= 400:
            log.error("Error while deleting index", url=url, resp=resp, index_name=index_name)
        
        # NOTE: create index
        body = mapping_template.render(
            field_type=field_type
        )

        url = f"{base_url}/{index_name}"
        resp = requests.put(url, auth=auth, headers=headers, verify=verify, data=body)
        if resp.status_code != 200:
            log.error("Error while creating mapping", url=url, resp=resp, field_type=field_type)

        # NOTE: add doc
        body = doc_template.render(
            field_value=field_value
        )
        url = f"{base_url}/{index_name}/_doc/1"
        resp = requests.put(url, auth=auth, headers=headers, verify=verify, data=body)
        if resp.status_code != 201:
            log.error("Error while indexing doc", url=url, resp=resp, index_name=index_name, field_type=field_type, field_value=field_value)
            
        url = f"{base_url}/{index_name}/_search"
        body = """
        {
            "fields": [
                "*"
            ],
            "_source": true
        }
        """
        resp = requests.get(url, auth=auth, headers=headers, verify=verify, data=body)
        
        text_resp = resp.text
        json_resp = json.loads(text_resp)
        
        # todo: something is wrong here. request from postman return hits, but not from here
        
        ignored_expr = parse("$.hits.hits[0]._ignored")
        res = ignored_expr.find(json_resp)
        if res and len(res) > 0:
            log.info("Ignored", result=json_resp)
        else:   
            output_expr = parse("$.hits.hits[0].fields.malformed_field")
            res = output_expr.find(json_resp)
            output = res[0]
            log.info("Not ignored", input=field_value, output=output)

