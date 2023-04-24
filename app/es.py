import os
from requests.auth import HTTPBasicAuth
import requests
import urllib3
import structlog
import curl

from app.template import Templates
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class Elasticsearch:
    def __init__(self) -> None:
        hostname = os.getenv("ELASTIC_HOSTNAME")
        self.verify = os.getenv("SSL_IGNORE_CERTIFICATE",
                                'True').lower() not in ('true', '1', 't')
        port = os.getenv("ELASTIC_PORT")

        username = os.getenv("ELASTIC_USERNAME")
        password = os.getenv("ELASTIC_PASSWORD")

        self.index_name = os.getenv("INDEX_NAME")

        self.auth = HTTPBasicAuth(username, password)
        self.headers = {
            "Content-Type": "application/json"
        }

        self.base_url = f"https://{hostname}:{port}"

        self.log = structlog.get_logger()
        
        self.templates = Templates()

    def ping(self):
        resp = requests.get(self.base_url,
                            auth=self.auth,
                            headers=self.headers,
                            verify=self.verify)
        assert resp.status_code == 200, "connection refused"

    def delete_index(self):
        url = f"{self.base_url}/{self.index_name}"
        resp = requests.delete(url,
                               auth=self.auth,
                               headers=self.headers,
                               verify=self.verify)
        if resp.status_code >= 400:
            self.log.error("Error while deleting index", url=url,
                           resp=resp, index_name=self.index_name)
        return resp.status_code

    def create_index(self, field_type):
        body = self.templates.mapping_template.render(
            field_type=field_type
        )
        
        url = f"{self.base_url}/{self.index_name}"
        resp = requests.put(url,
                            auth=self.auth,
                            headers=self.headers,
                            verify=self.verify,
                            data=body)
        if resp.status_code != 200:
            self.log.error("Error while creating mapping",
                           url=url, resp=resp, field_type=field_type)
            
        return resp.status_code

    def add_doc(self, field_type, field_value, id=1):
        body = self.templates.doc_template.render(
            field_value=field_value
        )
        
        url = f"{self.base_url}/{self.index_name}/_doc/{id}"
        resp = requests.put(url,
                            auth=self.auth,
                            headers=self.headers,
                            verify=self.verify,
                            data=body)
        if resp.status_code != 201:
            self.log.error("Error while indexing doc", url=url,
                           resp=resp,
                           index_name=self.index_name, 
                           field_type=field_type, 
                           field_value=field_value)
            
            cmd = curl.parse(resp, return_it=True, print_it=False)
            self.log.debug("Curl command", cmd=cmd)
        
        return resp.status_code
