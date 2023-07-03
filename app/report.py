from enum import Enum
import pandas as pd
from tabulate import tabulate


class TestStatus(str, Enum):
    skipped = "◻"

    passed = "☀️"

    ignored = "🌤️"

    failed = "⛈️"

    partially_failed = "☁️"


class Report:
    def __init__(self, columns) -> None:
        self.columns = columns
        self.index = [c for c in self.columns]

        self.n = len(self.columns)
        self.data = [None] * self.n

    def _summarize_results(self, data):
        summary = [None] * self.n
        counts = {
            "pass": 0,
            "fail": 0,
            "ignore": 0,
            "partial_fail": 0,
            "skip": 0,
            "total": 0,
        }

        for i in range(self.n):
            if not summary[i]:
                summary[i] = [None] * self.n  # init a new row
            
            for j in range(self.n):
                cell = data[i][j]
                total = cell["total"]
                skip = cell["skip"]

                counts["total"] += 1

                if skip > 0:
                    summary[i][j] = TestStatus.skipped
                    counts["skip"] += 1
                    continue

                not_skipped = total - skip

                if cell["pass"] == not_skipped:  # NOTE: all passed. none ignored
                    summary[i][j] = TestStatus.passed
                    counts["pass"] += 1
                elif cell["fail"] == not_skipped:  # NOTE: all failed. none ignored
                    summary[i][j] = TestStatus.failed
                    counts["fail"] += 1
                elif cell["fail"] == 0 and cell["ignore"] > 0:
                    summary[i][j] = TestStatus.ignored
                    counts["ignore"] += 1
                else:
                    summary[i][j] = TestStatus.partially_failed
                    counts["partial_fail"] += 1

        return summary, counts

    def get_legend(self):
        result = "Legend:\n"
        result += "\n".join([f"- {name}: {value}" for name,
                             value in TestStatus.__members__.items()])
        return result

    def summarize(self, output_file_path: str):
        summary, counts = self._summarize_results(self.data)
        df = pd.DataFrame(summary, columns=self.columns, index=self.index)

        result = tabulate(df, tablefmt="github", headers="keys")

        legend = self.get_legend()

        with open(output_file_path, "w") as fout:
            fout.write(result)
            fout.write("\n\n")
            fout.write(legend)
            
        return counts


    def save_to_json(self, output_file_path: str):
        df = pd.DataFrame(self.data, columns=self.columns, index=self.index)
        df.to_json(output_file_path)

    def init_result(self, i, j, total):
        if not self.data[i]:
            self.data[i] = [None] * self.n  # init a new row

        if not self.data[i][j]:
            # init a cell in n x n matrix
            self.data[i][j] = {"pass": 0,
                               "fail": 0,
                               "skip": 0,
                               "ignore": 0,
                               "total": total}

    def add_pass_result(self, i, j, n=1):
        self.data[i][j]["pass"] += n

    def add_fail_result(self, i, j, n=1):
        self.data[i][j]["fail"] += n

    def add_skip_result(self, i, j, n=1):
        self.data[i][j]["skip"] += n

    def add_ignored_result(self, i, j, n=1):
        self.data[i][j]["pass"] -= n
        self.data[i][j]["ignore"] += n
