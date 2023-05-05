import logging
from jsonpath_ng import jsonpath, parse
import os
from requests.auth import HTTPBasicAuth
import requests
import urllib3
import structlog
import curl
from structlog.contextvars import (
    bind_contextvars,
    # merge_contextvars,
    clear_contextvars,
)
from app.log import LogLevel, LogRenderer
from app.report import TestStatus

from app.template import Templates
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class Elasticsearch:
    def __init__(self, templates: Templates, log_level, log_renderer, enable_curl, include_resp) -> None:
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

        self.log_level = log_level
        structlog.configure(
            wrapper_class=structlog.make_filtering_bound_logger(
                LogLevel.to_int(self.log_level)),
            processors=[
                structlog.contextvars.merge_contextvars,
                structlog.processors.add_log_level,
                structlog.processors.StackInfoRenderer(),
                structlog.dev.set_exc_info,
                structlog.processors.TimeStamper(),
                LogRenderer.to_processor(log_renderer),
            ]
        )
        self.log = structlog.get_logger("es")

        clear_contextvars()

        self.include_resp = include_resp
        self.enable_curl = enable_curl

        self.templates = templates

    def _add_extra_context(self, resp):
        if self.include_resp:
            bind_contextvars(resp=resp.json())

        if self.enable_curl:
            curl_cmd = curl.parse(resp, return_it=True, print_it=False)
            bind_contextvars(curl=curl_cmd)

    def ping(self):
        resp = requests.get(self.base_url,
                            auth=self.auth,
                            headers=self.headers,
                            verify=self.verify)

        resp.raise_for_status()

        assert resp.status_code == 200, "connection refused"

    def delete_index(self):
        url = f"{self.base_url}/{self.index_name}"
        resp = requests.delete(url,
                               auth=self.auth,
                               headers=self.headers,
                               verify=self.verify)

        clear_contextvars()
        self._add_extra_context(resp)

        if resp.status_code >= 400:
            self.log.error("Error while deleting index")
        else:
            self.log.debug("Index deleted")

        clear_contextvars()
        return resp.status_code

    def create_index(self, mapping_type):
        body = self.templates.mapping_template.render(
            mapping_type=mapping_type
        ).replace("\n", "").replace(" ", "")

        clear_contextvars()
        bind_contextvars(mapping_type=mapping_type)

        url = f"{self.base_url}/{self.index_name}"
        resp = requests.put(url,
                            auth=self.auth,
                            headers=self.headers,
                            verify=self.verify,
                            data=body)

        self._add_extra_context(resp)

        if resp.status_code != 200:
            self.log.error("Error while creating mapping")
        else:
            self.log.debug("Created index")

        clear_contextvars()
        return resp.status_code

    def add_doc(self, mapping_type, runtime_type, value, id=1) -> TestStatus:
        body = self.templates.doc_template.render(
            value=value
        ).replace("\n", "").replace(" ", "")

        clear_contextvars()
        bind_contextvars(mapping_type=mapping_type,
                         runtime_type=runtime_type,
                         value=value)

        self.log.debug("Trying indexing...")

        url = f"{self.base_url}/{self.index_name}/_doc/{id}?refresh"
        resp = requests.put(url,
                            auth=self.auth,
                            headers=self.headers,
                            verify=self.verify,
                            data=body)

        self._add_extra_context(resp)

        result = TestStatus.skipped, 0

        if resp.status_code not in [201, 200]:
            self.log.error("Failed indexing doc")
            result = TestStatus.failed
        elif resp.status_code == 201 or resp.status_code == 200:
            self.log.debug("Object indexed correctly")
            result = TestStatus.passed

        clear_contextvars()
        return result

    def how_many_ignored(self) -> int:
        url = f"{self.base_url}/{self.index_name}/_search"
        body = {"query": {"exists": {"field": "_ignored"}}}

        resp = requests.get(url,
                            auth=self.auth,
                            headers=self.headers,
                            verify=self.verify,
                            json=body)

        resp.raise_for_status()

        json_resp = resp.json()

        hits_expr = parse("$.hits.total.value")
        number_hits = hits_expr.find(json_resp)
        if number_hits:
            return number_hits[0].value
        else:
            return 0
