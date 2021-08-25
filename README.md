# Metabase Import/Export

Export/Import metabase collection to JSON file.

Supports SQL native questions and dashboards. Snippets and non-SQL questions are currently not supported.

## Build and Install

```
python setup.py sdist
pip install dist/dist/metabase-import-export-0.2.3.tar.gz
```

## Usage

* See `metabase-import-export --help` for usage information.
* Export `metabase-import-export --username <username> --password <password> --url <url> export --collection-id <id> --export-file <file_name>.json `
* Import `metabase-import-export --username <username> --password <password> --url <url> import --collection-id <id> --import-file <file_name>.json`

## Environment Variables

| VAR                |
|--------------------|
| METABASE_USERNAME  |
| METABASE_PASSWORD  |
| METABASE_API_URL   |

## Usage with environment

You can set these environment variables before running.

* METABASE_USERNAME
* METABASE_PASSWORD
* METABASE_API_URL

* Export `metabase-import-export export --collection-id <id> --export-file <file_name>.json`
* Import `metabase-import-export import --collection-id <id> --import-file <file_name>.json`

## Docker 
Build dockerfile and run
``` 
docker build -t metabase-import-export .
docker run metabase-import-export --help
```
### Usage with docker

```
# metabase export
docker run metabase-import-export --username <username> --password <password> --url <url> \
 export --collection-id <id> --export-file <file_name>.json

# metabase import
docker run metabase-import-export --username <username> --password <password> --url <url> \
 import --collection-id <id> --import-file <file_name>.json
```

### Usage with environment variables

```
# metabase export
docker run -e "METABASE_USERNAME=username" \
           -e "METABASE_PASSWORD=password" \
           -e "METABASE_API_URL=url" \
           metabase-import-export  export --collection-id <id> --export-file <file_name>.json
 
# metabase import           
docker run -e "METABASE_USERNAME=username" \
           -e "METABASE_PASSWORD=password" \
           -e "METABASE_API_URL=url" \
           metabase-import-export import --collection-id <id> --import-file <file_name>.json
```

### Usage with env file

```
echo $'METABASE_USERNAME=username\nMETABASE_PASSWORD=password\nMETABASE_API_URL=url' > /path/to/data/.env

# metabase export
docker run --env-file=/path/to/data/.env \
           metabase-import-export  export --collection-id <id> --export-file <file_name>.json
 
# metabase import           
docker run --env-file=/path/to/data/.env \
           metabase-import-export import --collection-id <id> --import-file <file_name>.json
```


### Usage with bind volume

```
# metabase export
docker run --env-file=/path/to/data/.env \
           -v /path/to/data:/path/to/data \
           metabase-import-export  export --collection-id <id> --export-file /path/to/data/<file_name>.json
 
# metabase import           
docker run --env-file=/path/to/data/.env \
           -v /path/to/data/<file_name>.json:/path/to/data/<file_name>.json \
           metabase-import-export import --collection-id <id> --import-file /path/to/data/<file_name>.json
```



## License

This project is release under BSD license. See LICENSE.txt file for more information.
