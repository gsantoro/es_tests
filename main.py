from app.es import Elasticsearch
import structlog
import yaml
from app.log import LogBuilder, LogLevel, LogRenderer

from app.report import Report, TestStatus
import typer
from enum import Enum

from app.template import Templates


def main(
        test_file_path: str = typer.Argument(
            "data/tests/default.yaml", envvar="FILE_PATH", help="Path to test file"),
        include_same_type: bool = typer.Option(
            False, envvar="INCLUDE_SAME_TYPE", help="If you want to test <mapping_type>/<mapping_type> (eg. int/int)"),
        summarize: bool = typer.Option(True, envvar="SUMMARIZE", help="Wether to summarize the test from multiple values into a single status with weather icons or leave the raw data instead"),
        summary_output_file_path: str = typer.Option("summaries/default.md", envvar="SUMMARY_OUTPUT_FILE_PATH", help="Path to file to store summary"),
        log_level: LogLevel = typer.Option(LogLevel.info, envvar="LOG_LEVEL"),
        log_renderer: LogRenderer = typer.Option(LogRenderer.console, envvar="LOG_RENDERER"),
        include_curl: bool = typer.Option(False, envvar="INCLUDE_CURL", help="Whether to include the curl command in logs"),
        include_resp: bool = typer.Option(False, envvar="INCLUDE_RESPONSE", help="Whether to include the json response in logs"),
        report_output_file_path: str = typer.Option("reports/default.md", envvar="REPORT_OUTPUT_FILE_PATH", help="Path to file to store report"),
        templates_path: str = typer.Option("envs/app/data/templates", envvar="TEMPLATES_PATH", help="Where to find templates for ES requests"),
        mapping_template_name: str = typer.Option("ignore_malformed.mapping.txt", envvar="MAPPING_TEMPLATE_NAME", help="Name of the mapping template to use"),
        doc_template_name: str = typer.Option("doc.txt", envvar="DOC_TEMPLATE_NAME", help="Name of the doc template to use"),
):
    templates = Templates(templates_path, mapping_template_name, doc_template_name)
    es = Elasticsearch(templates, log_level, log_renderer, include_curl, include_resp)

    LogBuilder.configure(log_level=log_level, log_renderer=log_renderer)
    log = structlog.get_logger("main")

    log.info("Loading tests...", 
             file_path=test_file_path, 
             templates_path=templates_path, 
             mapping_template_name=mapping_template_name,
             doc_template_name=doc_template_name)

    with open(test_file_path) as f:
        mappings = yaml.safe_load(f)
        rows = mappings.keys()
        cols = mappings.keys()

        report = Report(rows)

        for i, mapping_type in enumerate(rows):
            log.debug("New mapping type", mapping_type=mapping_type)

            for j, runtime_type in enumerate(cols):
                values = mappings[runtime_type]
                n_values = len(values)
                report.init_result(i, j, n_values)

                if not include_same_type and i == j:
                    report.add_skip_result(i, j, n_values)
                    continue

                es.delete_index()
                    
                resp_status_code = es.create_index(mapping_type)
                if resp_status_code >= 300:
                    report.add_fail_result(i, j, n_values)
                    continue

                for id, value in enumerate(values):
                    test_status  = es.add_doc(mapping_type, runtime_type, value, id)

                    if test_status == TestStatus.failed:
                        report.add_fail_result(i, j)
                    elif test_status == TestStatus.passed:
                        report.add_pass_result(i, j)
                    
                n_ignored = es.how_many_ignored()
                if n_ignored > 0:
                    report.add_ignored_result(i, j, n_ignored)

        report.save_to_json(report_output_file_path)  

        if summarize:
            counts = report.summarize(summary_output_file_path)
            log.info("Counts", counts=counts)

if __name__ == "__main__":
    typer.run(main)
