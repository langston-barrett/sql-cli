#!/usr/bin/env python3

from argparse import ArgumentParser, Namespace
from enum import Enum, unique
from pathlib import Path
from sys import argv, stdout, stderr
from typing import Any, Callable, Dict, List
import csv
import json

import sqlalchemy as sa
import sqlalchemy.orm as orm


@unique
class Format(str, Enum):
    CSV = "csv"
    JSON = "json"
    JSONL = "jsonl"
    PRETTY = "pretty"
    TSV = "tsv"


@unique
class Operation(str, Enum):
    GET = "get"
    PUT = "put"
    RM = "rm"


def sql_to_python_type(sql_type: Any) -> Callable[[Any], Any]:
    # TODO: Improve bools
    # TODO: Handle other types
    if isinstance(sql_type, sa.Boolean):
        return bool
    if isinstance(sql_type, sa.Float):
        return float
    if isinstance(sql_type, sa.Numeric):
        return float
    if isinstance(sql_type, sa.Integer):
        return int
    if isinstance(sql_type, sa.String):
        return str
    if isinstance(sql_type, sa.Text):
        return str
    return lambda x: x


def add_get(sub: Any, table: sa.Table) -> None:
    get = sub.add_parser(Operation.GET.value)
    get.add_argument("--format", default=Format.CSV, type=Format)
    for col in table.columns:
        py_type = sql_to_python_type(col.type)
        kwargs: Dict[str, Any] = {
            "action": "append",
            "default": [],
            "metavar": col.name.upper()[:4],
        }

        if py_type == int:
            kwargs["type"] = py_type
            kwargs["help"] = f"type: {py_type.__name__}"
        if py_type == bool:
            kwargs["choices"] = ["t", "f"]
            kwargs["help"] = f"type: {py_type.__name__}"

        get.add_argument(f"--{col.name}-is", **kwargs)
        get.add_argument(f"--{col.name}-not", **kwargs)
        if py_type == int:
            # TODO
            # get.add_argument(f"--{col.name}-gt", **kwargs)
            # get.add_argument(f"--{col.name}-lt", **kwargs)
            pass
        if py_type == str:
            # TODO
            # get.add_argument(f"--{col.name}-like", **kwargs)
            # get.add_argument(f"--{col.name}-matches", **kwargs)
            pass

    # get.print_help()


def add_put(sub: Any, table: sa.Table) -> None:
    put = sub.add_parser(Operation.PUT.value)


def create_parser(metadata: sa.MetaData, parser: ArgumentParser) -> None:
    top_level_subparsers = parser.add_subparsers(
        dest="table", help="table", required=True
    )
    for table in metadata.tables.values():
        help = f"The {table.name} table. Primary key(s): {', '.join(t.name for t in table.primary_key)}"
        sub = top_level_subparsers.add_parser(
            table.name, description=help, help=f"The {table.name} table"
        )
        sub_subparsers = sub.add_subparsers(
            dest="operation", help="operation", required=True
        )
        add_get(sub_subparsers, table)
        add_put(sub_subparsers, table)


def get_query(session: orm.Session, table: sa.Table, args: Namespace) -> orm.Query:
    q = session.query(table)
    for arg, val in vars(args).items():
        if arg.endswith("_is") and isinstance(val, list) and val != []:
            q = q.filter(table.c[arg[: -len("_is")]].in_(val))
        elif arg.endswith("_not") and isinstance(val, list) and val != []:
            q = q.filter(table.c[arg[: -len("_not")]].notin_(val))
        # TODO: gt
        # TODO: lt
    return q


def format_query(query: orm.Query, fmt: Format) -> None:
    if fmt == Format.CSV or fmt == Format.TSV:
        w = csv.writer(stdout, delimiter="\t" if fmt == Format.TSV else ",")
        for row in query.all():
            w.writerow(row)
    elif fmt == Format.JSONL or fmt == Format.PRETTY:
        for row in query.all():
            obj = dict()
            assert len(row) == len(query.column_descriptions)
            for (col, val) in zip(query.column_descriptions, row):
                obj[col["name"]] = val
            print(json.dumps(obj, indent=2 if fmt == Format.PRETTY else None))
    else:
        assert False


def do_get(
    metadata: sa.MetaData, session: orm.Session, table_name: str, args: Namespace
) -> None:
    table = metadata.tables[table_name]
    query = get_query(session, table, args)
    format_query(query, args.format)


def sql_cli_main(
    db_file: Path,
    args: List[str],
    parser: ArgumentParser = ArgumentParser(
        prog="sql-cli",
        description="Dynamically generate CLIs from SQL databases that support CRUD operations",
    ),
    /,
) -> int:
    if not db_file.exists():
        print(f"No database at {db_file}", file=stderr)
        return 1
    engine = sa.create_engine(f"sqlite:///{str(db_file.absolute())}")
    metadata = sa.MetaData()
    metadata.reflect(engine)

    create_parser(metadata, parser)
    parsed_args = parser.parse_args(args=args)

    Session = orm.sessionmaker(engine)
    with Session() as session:
        if parsed_args.operation == Operation.GET.value:
            do_get(metadata, session, parsed_args.table, parsed_args)
    return 0
