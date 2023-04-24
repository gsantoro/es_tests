from app.es import Elasticsearch
import structlog
import yaml
from app.log import LogLevel

from app.report import Report
import typer
from enum import Enum

es = Elasticsearch()


def main(
        file_path: str = typer.Argument(
            "data/tests/default.yaml", envvar="FILE_PATH"),
        include_same_type: bool = typer.Option(
            False, envvar="INCLUDE_SAME_TYPE"),
        summarize: bool = typer.Option(True, envvar="SUMMARIZE"),
        log_level: LogLevel = typer.Option(LogLevel.info, envvar="LOG_LEVEL")
):

    structlog.configure(
        wrapper_class=structlog.make_filtering_bound_logger(
            LogLevel.to_int(log_level))
    )
    log = structlog.get_logger()

    log.info("Loading tests...", file_path=file_path)

    with open(file_path) as f:
        fields = yaml.safe_load(f)

        report = Report(fields.keys())

        for i, type_i in enumerate(fields.keys()):
            for j, type_j in enumerate(fields.keys()):
                values = fields[type_j]
                report.init_result(i, j, len(values))

                if not include_same_type and i == j:
                    report.skip_result(i, j)
                    continue

                es.delete_index()
                es.create_index(type_i)

                for id, value in enumerate(values):
                    log.debug("Trying indexing...", type_i=type_i,
                              type_j=type_j, value=value)
                    status = es.add_doc(type_i, value, id=id)

                    if status == 201:
                        report.add_pass_result(i, j)
                    else:
                        report.add_fail_result(i, j)

        if summarize:
            report.summarize()
        report.markdown_table()


if __name__ == "__main__":
    typer.run(main)
