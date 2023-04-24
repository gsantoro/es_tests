from app.es import Elasticsearch
import structlog
import yaml
from app.log import LogLevel

from app.report import Report
import typer
from enum import Enum


def main(
        file_path: str = typer.Argument(
            "data/tests/default.yaml", envvar="FILE_PATH"),
        include_same_type: bool = typer.Option(
            False, envvar="INCLUDE_SAME_TYPE"),
        summarize: bool = typer.Option(True, envvar="SUMMARIZE"),
        log_level: LogLevel = typer.Option(LogLevel.info, envvar="LOG_LEVEL"),
        enable_curl: bool = typer.Option(False, envvar="ENABLE_CURL"),
        include_resp: bool = typer.Option(False, envvar="INCLUDE_RESPONSE"),
):
    es = Elasticsearch(log_level, enable_curl, include_resp)

    structlog.configure(
        wrapper_class=structlog.make_filtering_bound_logger(
            LogLevel.to_int(log_level))
    )
    log = structlog.get_logger("main")

    log.info("Loading tests...", file_path=file_path)

    with open(file_path) as f:
        mappings = yaml.safe_load(f)

        report = Report(mappings.keys())

        for i, mapping_type in enumerate(mappings.keys()):
            log.debug("New mapping type", mapping_type=mapping_type)

            for j, runtime_type in enumerate(mappings.keys()):
                values = mappings[runtime_type]
                report.init_result(i, j, len(values))

                if not include_same_type and i == j:
                    report.skip_result(i, j)
                    continue

                es.delete_index()
                es.create_index(mapping_type)

                for id, value in enumerate(values):
                    status = es.add_doc(mapping_type, runtime_type, value, id)

                    if status == 201:
                        report.add_pass_result(i, j)
                    else:
                        report.add_fail_result(i, j)

        if summarize:
            counts = report.summarize()
            log.info("Counts", counts=counts)
        report.markdown_table()


if __name__ == "__main__":
    typer.run(main)
