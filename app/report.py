import pandas as pd

class Report:
    def __init__(self, columns) -> None:
        self.columns = columns
        self.index = [f"type: {c}" for c in self.columns]
        
        self.n = len(self.columns)
        self.data = [None] * self.n
        
    def summarize(self):
        for i in range(self.n):
            for j in range(self.n):
                results = self.data[i][j]
                total = results["total"]
                skip = results["skip"]
                if skip > 0:
                    self.data[i][j] = "-"
                    continue
                
                if results["pass"] == total - skip:
                    self.data[i][j] = "✅"
                elif results["fail"] == total - skip:
                    self.data[i][j] = "❌"
                else:
                    self.data[i][j] = "❓" # NOTE: partial failures
                
        
    def markdown_table(self):
        df = pd.DataFrame(self.data, columns=self.columns, index=self.index)

        print(df.to_markdown(tablefmt="grid"))
        
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