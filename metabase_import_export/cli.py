#!/usr/bin/env python

import argparse

from . import run_import, run_export, metabase_login, set_metabase_url


def get_argparser():

    parser = argparse.ArgumentParser(
        description="Export/Import metabase collection to JSON file.",
        epilog=(
            "Supports SQL native questions and dashboards. Snippets and non-SQL "
            "questions are currently not supported."
        ),
    )
    parser.add_argument(
        "--username",
        help="Metabase admin user",
        required=True,
    )
    parser.add_argument(
        "--url",
        help="Metabase base URL",
        default="http://localhost:3000",
    )

    subparsers = parser.add_subparsers()

    # Export sub-parser
    export_parser = subparsers.add_parser("export")
    export_parser.add_argument(
        "--collection-id",
        type=int,
        help="The id of the collection to be exported.",
        required=True,
    )
    export_parser.add_argument(
        "--export-file",
        help="File path to store the export data in JSON format.",
        required=True,
    )
    export_parser.set_defaults(func=run_export)

    # Import sub-parser
    import_parser = subparsers.add_parser("import")
    import_parser.add_argument(
        "--collection-id",
        type=int,
        help="The id of the collection where the data will be imported to.",
        required=True,
    )
    import_parser.add_argument(
        "--import-file",
        help="File path to import the data from.",
        required=True,
    )
    import_parser.set_defaults(func=run_import)

    return parser


def main():
    parser = get_argparser()
    args = parser.parse_args()

    set_metabase_url(args.url)
    metabase_login(args.username)

    if hasattr(args, "func"):
        args.func(args)
    else:
        parser.print_usage()


if __name__ == "__main__":
    main()
