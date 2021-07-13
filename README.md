# Metabase Import/Export

Export/Import metabase collection to JSON file.

Supports SQL native questions and dashboards. Snippets and non-SQL questions are currently not supported.

## Build

* `python setup.py sdist`

## Install

* `pip install metabase-import-export`

## Usage

* See `metabase-import-export --help` for usage information.
* Export `metabase-import-export --username <username> --password <password> --url <url> export --collection-id <id> --export-file <file_name>.json `
* Import `metabase-import-export --username <username> --password <password> --url <url> import --collection-id <id> --import-file <file_name>.json`

## Usage with environment

You can set these environment variables before running.

* METABASE_USERNAME
* METABASE_PASSWORD
* METABASE_API_URL

* Export `metabase-import-export export --collection-id <id> --export-file <file_name>.json`
* Import `metabase-import-export import --collection-id <id> --import-file <file_name>.json`

## License

This project is release under BSD license. See LICENSE.txt file for more information.
