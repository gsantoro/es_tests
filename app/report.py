from enum import Enum
import pandas as pd
from tabulate import tabulate


class Symbols(str, Enum):
    test_skip = "◻️"
    test_pass = "✅"
    test_fail = "❌"
    test_partial_fail = "❓"


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
                    self.data[i][j] = Symbols.test_skip
                    counts["skip"] += 1
                    continue

                if results["pass"] == total - skip:
                    self.data[i][j] = Symbols.test_pass
                    counts["pass"] += 1
                elif results["fail"] == total - skip:
                    self.data[i][j] = Symbols.test_fail
                    counts["fail"] += 1
                else:
                    self.data[i][j] = Symbols.test_partial_fail
                    counts["partial_fail"] += 1
                    
        return counts

    def markdown_table(self):
        df = pd.DataFrame(self.data, columns=self.columns, index=self.index)

        tablefmt = self.report_format.lower()
        result = tabulate(df, tablefmt=tablefmt, headers="keys")

        if self.output == ReportOutput.file:
            with open(self.output_file_path, "w") as fout:
                fout.write(result)
        else:
            print(result)

    def init_result(self, i, j, total):
        if not self.data[i]:
            self.data[i] = [None] * self.n

        if not self.data[i][j]:
            self.data[i][j] = {"pass": 0, "fail": 0, "skip": 0, "total": total}

    def add_pass_result(self, i, j):
        self.data[i][j]["pass"] += 1

    def add_fail_result(self, i, j):
        self.data[i][j]["fail"] += 1

    def skip_result(self, i, j):
        self.data[i][j]["skip"] += 1
