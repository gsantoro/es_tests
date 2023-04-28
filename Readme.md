# Readme

This project is an attempt to test the effect of introducing the parameter `ignore_malformed` to the default template settings in Elasticsearch.

## How to run

This project has many requirements. The easiest way to develop without installing all those requirements is using VSCode as suggested [here](https://code.visualstudio.com/docs/devcontainers/containers).
In short from inside VScode you can clone this github repo into a named container volume to develop inside a devcontainer.

Once you have your devcontainer running you need to issue the following commands:

```bash
cd envs/app  # loads env environment thanks to direnv
task elastic:up  # start elastic stack using elastic-package in a docker container
task poetry:run  # run the report
```

you can customize different parameters by changing the environment variables defined at `envs/app/.env`

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
  --log-renderer [CONSOLE|JSON]   [env var: LOG_RENDERER; default:
                                  LogRenderer.console]
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

## Reports

Multiple reports can be found at `./reports/*.md` and the corresponding logs are at `./logs/*.log`.

These are the current results

- everything with `ignore_malformed=true`

  - mapping: `envs/app/data/templates/ignore_malformed.mapping.txt`
  - test: `envs/app/data/tests/everything.yaml`
  - report: `reports/everything.ignore_malformed.md`
  - summary: `{"pass": 115, "fail": 210, "ignore": 139, "partial_fail": 42, "skip": 23, "total": 529}`

- everything with no settings
  - mapping: `envs/app/data/templates/no_settings.mapping.txt`
  - test: `envs/app/data/tests/everything.yaml`
  - report: `reports/everything.no_settings.md`
  - summary: `{"pass": 115, "fail": 343, "ignore": 0, "partial_fail": 48, "skip": 23, "total": 529}`

From all the available Elasticsearch [types](https://www.elastic.co/guide/en/elasticsearch/reference/current/mapping-types.html), these are the types that I have skipped from the current test and the reason for skipping them

these types are mostly redundant since we test similar types

- long
- short
- float
- half_float
- scaled_float
- unsigned_logs
- long_range
- double_range
- shape
- geo_shape

the following instead are either hard to test (like they require a special plugin or they need a special config) or not very common

- alias
- join
- murmur3
- aggregate_metric_double
- annotated-text
- completion
- search_as_you_type
- token_count
- dense_vector
- rank_feature
- rank_features
- percolator
