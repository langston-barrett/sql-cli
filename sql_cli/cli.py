from argparse import ArgumentParser, Namespace
from enum import Enum, unique
from pathlib import Path
from sys import argv, stdout, stderr

from sql_cli import sql_cli_main


def main() -> None:
    if len(argv) < 2:
        print("Usage: sql-cli DB")
        exit(1)
    try:
        exit(sql_cli_main(Path(argv[1]), argv[2:]))
    except Exception as e:
        print("Unknown error!", file=stderr)
        raise e


if __name__ == "__main__":
    main()
