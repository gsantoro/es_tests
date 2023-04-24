import pandas as pd
from tabulate import tabulate


class Symbols:
    test_skip = "◻️"
    test_pass = "✅"
    test_fail = "❌"
    test_partial_fail = "❓"


class Report:
    def __init__(self, columns) -> None:
        self.columns = columns
        self.index = [f"type: {c}" for c in self.columns]

        self.n = len(self.columns)
        self.data = [None] * self.n

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

        print(tabulate(df, tablefmt="grid", headers="keys"))

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
