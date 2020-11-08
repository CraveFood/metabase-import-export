
import getpass
import json
import requests
import sys
from copy import deepcopy

METABASE_CONFIG = {}

DATABASES_CACHE = []
EXPORT_IMPORT_MAPPING = {}
DB_MAPPING = {}
TABLE_MAPPING = {}
FIELD_MAPPING = {}

SESSION = requests.Session()


def set_metabase_url(url):
    METABASE_CONFIG["url"] = url


def call_api(method, uri, json=None, params=None):
    url = METABASE_CONFIG["url"] + uri
    response = SESSION.request(
        method,
        url,
        json=json,
        params=params,
    )
    if response.status_code == requests.codes.not_found:
        print("Not found: {}".format(url))
    elif not 200 <= response.status_code < 300:
        print(response.content.decode("utf-8"))
    return response.json()


def metabase_login(username):
    password = getpass.getpass("Password for user {}: ".format(username))

    login_url = "/api/session"
    data = {
        "username": username,
        "password": password,
        "remember": False,
    }
    login_response = call_api("post", login_url, json=data)
    if "errors" in login_response:
        print("Failed to login in Metabase")
        sys.exit(1)


def get_card(card_id):
    api_card_url = "/api/card/{}".format(card_id)
    return call_api("get", api_card_url)


def list_collections():
    api_list_collections_url = "/api/collection/"
    return call_api("get", api_list_collections_url)


def get_collection_items(collection_id):
    api_collection_items_url = "/api/collection/{}/items".format(collection_id)
    return call_api("get", api_collection_items_url)


def get_dashboard(dashboard_id):
    api_dashboard_url = "/api/dashboard/{}".format(dashboard_id)
    return call_api("get", api_dashboard_url)


def list_databases():
    api_db_url = "/api/database/"
    return call_api("get", api_db_url)


def get_database(db_id):
    if DATABASES_CACHE:
        return DATABASES_CACHE

    api_db_url = "/api/database/{}".format(db_id)
    dbs = call_api("get", api_db_url, params={"include": "tables.fields"})
    DATABASES_CACHE.extend(dbs)
    return dbs


def get_mapping_db(database_id):
    mapped_id = DB_MAPPING.get(database_id)
    if mapped_id is None:
        print("Database '{}' was not mapped.".format(database_id))
        sys.exit(1)
    return mapped_id


def create_card(card, **kwargs):
    api_card_url = "/api/card"
    data = deepcopy(card)
    data.update(kwargs)

    data["database_id"] = get_mapping_db(data["database_id"])
    data["dataset_query"]["database"] = get_mapping_db(
        data["dataset_query"]["database"],
    )

    if data["table_id"] is not None:
        data["table_id"] = TABLE_MAPPING[data["table_id"]]

    if data["dataset_query"]["type"] == "native":
        for tag in data["dataset_query"]["native"]["template-tags"].values():
            if "dimension" in tag and tag["dimension"][0] == "field-id":
                tag["dimension"][1] = FIELD_MAPPING[tag["dimension"][1]]

    new_card = call_api("post", api_card_url, json=data)
    EXPORT_IMPORT_MAPPING[card["id"]] = new_card["id"]

    return new_card


def replace_card_ids(obj_dict, id_key="card_id"):
    new_obj_dict = deepcopy(obj_dict)
    for item in new_obj_dict:
        new_card_id = EXPORT_IMPORT_MAPPING[item[id_key]]
        item[id_key] = new_card_id
    return new_obj_dict


def create_dashboard(dashboard, **kwargs):
    api_dashboard_url = "/api/dashboard"
    data = deepcopy(dashboard)
    data.update(kwargs)

    for field in data["param_fields"].values():
        field["table_id"] = TABLE_MAPPING[field["table_id"]]

    new_dashboard = call_api("post", api_dashboard_url, json=data)

    api_add_card_to_dashboard = "{}/{}/cards".format(
        api_dashboard_url,
        new_dashboard["id"],
    )
    for card in dashboard["ordered_cards"]:
        if card["card_id"] not in EXPORT_IMPORT_MAPPING:
            print(
                "Card '{}' was not imported and it's trying "
                "to be added to an imported dashboard".format(card["card_id"])
            )
            sys.exit(1)
            continue

        new_card_id = EXPORT_IMPORT_MAPPING[card["card_id"]]
        parameter_mappings = replace_card_ids(card["parameter_mappings"])
        series = replace_card_ids(card["series"], "id")

        data = {
            "cardId": new_card_id,
            "parameter_mappings": parameter_mappings,
            "series": series,
            "visualization_settings": card["visualization_settings"],
            "sizeX": card["sizeX"],
            "sizeY": card["sizeY"],
            "row": card["row"],
            "col": card["col"],
        }
        call_api("post", api_add_card_to_dashboard, json=data)


def export_databases(collection_items):
    database_ids = set()
    for item in collection_items:
        if item["model"] == "card":
            database_ids.add(item["data"]["database_id"])
            database_ids.add(item["data"]["dataset_query"]["database"])

    database_ids.discard(None)

    databases = []
    for db_id in database_ids:
        databases.append(get_database(db_id))

    return databases


def check_if_collection_exists(collection_id):
    collections = list_collections()
    for collection in collections:
        if collection["id"] == collection_id:
            collection_id = collection["id"]
            break
    else:
        print("Collection with id '{}' not found.".format(collection_id))
        sys.exit(1)


def export_collection(file_path, collection_id):
    check_if_collection_exists(collection_id)

    collection_items = get_collection_items(collection_id)
    for item in collection_items:
        model = item["model"]
        id = item["id"]

        if model == "card":
            data = get_card(id)
        elif model == "dashboard":
            data = get_dashboard(id)
        item["data"] = data

    databases = export_databases(collection_items)

    export_data = {
        "collection_items": collection_items,
        "databases": databases,
    }

    with open(file_path, "w") as export_file:
        json.dump(export_data, export_file, indent=2)

    return collection_items


def get_db_names(data, source):
    return ["{} ({} - {})".format(db["name"], db["id"], source) for db in data]


def map_databases(exported_databases):
    dbs = list_databases()

    print(
        "\nTo import the data to Metabase you will need to "
        "select the database where you want the data to be imported to.\n"
    )
    db_ids = [db["id"] for db in dbs]
    for exported_db in exported_databases:
        while True:
            print(
                "Select the database where you want to import the data exported "
                "from the database '{}'.\n".format(exported_db["name"])
            )
            for db in dbs:
                print("{} - {}".format(db["id"], db["name"]))

            print("")
            selection = input("\n>>> ")

            try:
                if int(selection) in db_ids:
                    DB_MAPPING[exported_db["id"]] = int(selection)
                    break
                else:
                    print("\n*** Invalid selection ***\n")
            except ValueError:
                print("\n** Invalid selection **\n")


def load_database_mapping(exported_databases):
    map_databases(exported_databases)

    exported_db_ids = {db["id"] for db in exported_databases}
    db_ids = DB_MAPPING.values()

    diff_exported_to_mapped = exported_db_ids - set(DB_MAPPING.keys())
    if diff_exported_to_mapped:
        print(
            "All exported DBs needs to be mapped to be imported. "
            "The DBs '{}' are not mapped.".format(diff_exported_to_mapped),
        )
        sys.exit(1)

    databases = []
    tables = []
    fields = []

    for db_id in db_ids:
        database = get_database(db_id)
        databases.append(database)

        tables.extend(database["tables"])
        for table in database["tables"]:
            fields.extend(table["fields"])

    for exported_db in exported_databases:
        for exported_table in exported_db["tables"]:
            for table in tables:
                if (
                    table["name"] == exported_table["name"]
                    and table["db_id"] == DB_MAPPING[exported_db["id"]]
                ):
                    TABLE_MAPPING[exported_table["id"]] = table["id"]
                    break

            else:
                print(
                    "Table '{}' doesn't exist on db '{}'.".format(
                        exported_table["name"],
                        DB_MAPPING[exported_db["id"]],
                    )
                )
                sys.exit(1)

            for exported_field in exported_table["fields"]:
                for field in fields:
                    if (
                        field["name"] == exported_field["name"]
                        and field["table_id"] == TABLE_MAPPING[exported_table["id"]]
                    ):
                        FIELD_MAPPING[exported_field["id"]] = field["id"]
                        break

                else:
                    print(
                        "Field '{}' doesn't exist on table '{}'.".format(
                            exported_table["name"], TABLE_MAPPING[exported_table["id"]]
                        )
                    )
                    sys.exit(1)


def import_collection(export_file, collection_id):
    check_if_collection_exists(collection_id)

    with open(export_file) as export_file:
        export_data = json.load(export_file)

    load_database_mapping(export_data["databases"])

    for item in export_data["collection_items"]:
        if item["model"] == "card":
            create_card(item["data"], collection_id=collection_id)

    for item in export_data["collection_items"]:
        if item["model"] == "dashboard":
            create_dashboard(item["data"], collection_id=collection_id)


def run_import(args):
    import_collection(args.import_file, args.collection_id)


def run_export(args):
    export_collection(args.export_file, args.collection_id)
