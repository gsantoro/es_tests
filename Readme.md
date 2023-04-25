# Readme

Results from the tests are available under the folder `reports`:
- 

## Legend
- skipped = "◻"
  - skipped tests. This can be controlled by `INCLUDE_SAME_TYPE`
- passed = "☀️"
  - indexing worked for all values for this combination of mapping type and runtime type without ignored fields
- ignored = "🌤️"
  - no failures but some values were ignored
- failed = "⛈️"
  - indexing failed for all values combination of mapping type and runtime type 
- partially_failed = "☁️"
  - some values for this type failed, some others might have passed or may have been ignored


## Usage
```bash
Usage: main.py [OPTIONS] [FILE_PATH]

Arguments:
  [FILE_PATH]  Path to test file  [env var: FILE_PATH;default:
               data/tests/default.yaml]

Options:
  --include-same-type / --no-include-same-type
                                  If you want to test
                                  <mapping_type>/<mapping_type> (eg. int/int)
                                  [env var: INCLUDE_SAME_TYPE; default: no-
                                  include-same-type]
  --summarize / --no-summarize    Wether to summarize the test from multiple
                                  values into a single status  [env var:
                                  SUMMARIZE; default: summarize]
  --log-level [CRITICAL|FATAL|ERROR|WARNING|WARN|INFO|DEBUG|NOTSET]
                                  [env var: LOG_LEVEL; default: LogLevel.info]
  --include-curl / --no-include-curl
                                  Whether to include the curl command in logs
                                  [env var: INCLUDE_CURL; default: no-include-
                                  curl]
  --include-resp / --no-include-resp
                                  Whether to include the json response in logs
                                  [env var: INCLUDE_RESPONSE; default: no-
                                  include-resp]
  --report-output [TERMINAL|FILE]
                                  Where to send the report output  [env var:
                                  REPORT_OUTPUT; default: TERMINAL]
  --report-output-file-path TEXT  Path to file to store report  [env var:
                                  REPORT_OUTPUT_FILE_PATH; default:
                                  reports/default.md]
  --report-format TEXT            Which format to use for the report  [env
                                  var: REPORT_FORMAT; default: GITHUB]
  --templates-path TEXT           Where to find templates for ES requests
                                  [env var: TEMPLATES_PATH; default:
                                  envs/app/data/templates]
  --mapping-template-name TEXT    Name of the mapping template to use  [env
                                  var: MAPPING_TEMPLATE_NAME; default:
                                  ignore_malformed.mapping.txt]
  --doc-template-name TEXT        Name of the doc template to use  [env var:
                                  DOC_TEMPLATE_NAME; default: doc.txt]
  --help                          Show this message and exit.
```


## Findings
- everything with `ignore_malformed=true`
  - mapping: `envs/app/data/templates/ignore_malformed.mapping.txt`
  - test: `envs/app/data/tests/everything.yaml`
  - report: `reports/everything.ignore_malformed.md`
  - summary: `{'pass': 97, 'fail': 138, 'ignore': 108, 'partial_fail': 37, 'skip': 20, 'total': 400}`


- everything with no settings
  - mapping: `envs/app/data/templates/no_settings.mapping.txt`
  - test: `envs/app/data/tests/everything.yaml`
  - report: `reports/everything.no_settings.md`
  - summary: `{'pass': 97, 'fail': 241, 'ignore': 0, 'partial_fail': 42, 'skip': 20, 'total': 400}`