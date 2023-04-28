from enum import Enum
import pandas as pd
from tabulate import tabulate


class TestStatus(str, Enum):
    skipped = "◻"

    passed = "☀️"

    ignored = "🌤️"

    failed = "⛈️"

    partially_failed = "☁️"


class ReportOutput(str, Enum):
    terminal = "TERMINAL"
    file = "FILE"


class ReportFormat(str, Enum):
    grid = "GRID"
    github = "GITHUB"


class Report:
    def __init__(self, columns, output: ReportOutput, output_file_path: str, report_format: ReportFormat) -> None:
        self.columns = columns
        self.index = [f"type: {c}" for c in self.columns]

        self.n = len(self.columns)
        self.data = [None] * self.n

        self.output = output
        self.output_file_path = output_file_path

        self.report_format = report_format

    def summarize(self):
        counts = {
            "pass": 0,
            "fail": 0,
            "ignore": 0,
            "partial_fail": 0,
            "skip": 0,
            "total": 0,
        }

        for i in range(self.n):
            for j in range(self.n):
                results = self.data[i][j]
                total = results["total"]
                skip = results["skip"]

                counts["total"] += 1

                if skip > 0:
                    self.data[i][j] = TestStatus.skipped
                    counts["skip"] += 1
                    continue

                if results["pass"] == total - skip:  # NOTE: all passed. none ignored
                    self.data[i][j] = TestStatus.passed
                    counts["pass"] += 1
                elif results["fail"] == total - skip:  # NOTE: all failed. none ignored
                    self.data[i][j] = TestStatus.failed
                    counts["fail"] += 1
                elif results["fail"] == 0 and results["ignore"] > 0:
                    self.data[i][j] = TestStatus.ignored
                    counts["ignore"] += 1
                else:
                    self.data[i][j] = TestStatus.partially_failed
                    counts["partial_fail"] += 1

        return counts

    def get_legend(self):
        result = "Legend:\n"
        result += "\n".join([f"- {name}: {value}" for name,
                   value in TestStatus.__members__.items()])
        return result

    def print_results(self):
        df = pd.DataFrame(self.data, columns=self.columns, index=self.index)

        tablefmt = self.report_format.lower()
        result = tabulate(df, tablefmt=tablefmt, headers="keys")

        legend = self.get_legend()

        if self.output == ReportOutput.file:
            with open(self.output_file_path, "w") as fout:
                fout.write(result)
                fout.write("\n\n")
                fout.write(legend)
        else:
            print(result)
            print("\n\n")
            print(legend)

    def init_result(self, i, j, total):
        if not self.data[i]:
            self.data[i] = [None] * self.n

        if not self.data[i][j]:
            self.data[i][j] = {"pass": 0,
                               "fail": 0,
                               "skip": 0,
                               "ignore": 0,
                               "total": total}

    def add_pass_result(self, i, j):
        self.data[i][j]["pass"] += 1

    def add_fail_result(self, i, j):
        self.data[i][j]["fail"] += 1

    def add_skip_result(self, i, j):
        self.data[i][j]["skip"] += 1

    def add_ignored_result(self, i, j, number_ignored):
        self.data[i][j]["pass"] -= number_ignored
        self.data[i][j]["ignore"] += number_ignored
