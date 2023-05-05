from app.es import Elasticsearch
import structlog
import yaml
from app.log import LogLevel, LogRenderer

from app.report import ReportOutput, Report, TestStatus
import typer
from enum import Enum

from app.template import Templates


def main(
        file_path: str = typer.Argument(
            "data/tests/default.yaml", envvar="FILE_PATH", help="Path to test file"),
        include_same_type: bool = typer.Option(
            False, envvar="INCLUDE_SAME_TYPE", help="If you want to test <mapping_type>/<mapping_type> (eg. int/int)"),
        summarize: bool = typer.Option(True, envvar="SUMMARIZE", help="Wether to summarize the test from multiple values into a single status"),
        log_level: LogLevel = typer.Option(LogLevel.info, envvar="LOG_LEVEL"),
        log_renderer: LogRenderer = typer.Option(LogRenderer.console, envvar="LOG_RENDERER"),
        include_curl: bool = typer.Option(False, envvar="INCLUDE_CURL", help="Whether to include the curl command in logs"),
        include_resp: bool = typer.Option(False, envvar="INCLUDE_RESPONSE", help="Whether to include the json response in logs"),
        report_output: ReportOutput = typer.Option("TERMINAL", envvar="REPORT_OUTPUT", help="Where to send the report output"),
        report_output_file_path: str = typer.Option("reports/default.md", envvar="REPORT_OUTPUT_FILE_PATH", help="Path to file to store report"),
        report_format: str = typer.Option("GITHUB", envvar="REPORT_FORMAT", help="Which format to use for the report"),
        templates_path: str = typer.Option("envs/app/data/templates", envvar="TEMPLATES_PATH", help="Where to find templates for ES requests"),
        mapping_template_name: str = typer.Option("ignore_malformed.mapping.txt", envvar="MAPPING_TEMPLATE_NAME", help="Name of the mapping template to use"),
        doc_template_name: str = typer.Option("doc.txt", envvar="DOC_TEMPLATE_NAME", help="Name of the doc template to use"),
):
    templates = Templates(templates_path, mapping_template_name, doc_template_name)
    es = Elasticsearch(templates, log_level, log_renderer, include_curl, include_resp)

    structlog.configure(
        wrapper_class=structlog.make_filtering_bound_logger(
            LogLevel.to_int(log_level))
    )
    log = structlog.get_logger("main")

    log.info("Loading tests...", 
             file_path=file_path, 
             templates_path=templates_path, 
             mapping_template_name=mapping_template_name,
             doc_template_name=doc_template_name)

    with open(file_path) as f:
        mappings = yaml.safe_load(f)

        report = Report(mappings.keys(), report_output, report_output_file_path, report_format)

        for i, mapping_type in enumerate(mappings.keys()):
            log.debug("New mapping type", mapping_type=mapping_type)

            for j, runtime_type in enumerate(mappings.keys()):
                values = mappings[runtime_type]
                report.init_result(i, j, len(values))

                if not include_same_type and i == j:
                    report.add_skip_result(i, j)
                    continue

                es.delete_index()
                    
                resp_status_code = es.create_index(mapping_type)
                if resp_status_code >= 300:
                    for _, _ in enumerate(values):
                        report.add_fail_result(i, j)
                    continue

                for id, value in enumerate(values):
                    test_status  = es.add_doc(mapping_type, runtime_type, value, id)

                    if test_status == TestStatus.failed:
                        report.add_fail_result(i, j)
                    elif test_status == TestStatus.passed:
                        report.add_pass_result(i, j)
                    
                number_ignored = es.how_many_ignored()
                if number_ignored > 0:
                    report.add_ignored_result(i, j, number_ignored)

        if summarize:
            counts = report.summarize()
            log.info("Counts", counts=counts)
        report.print_results()


if __name__ == "__main__":
    typer.run(main)
