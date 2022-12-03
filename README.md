# sql-cli

sql-cli dynamically generates CLIs from SQL databases that support CRUD
(create, read, update, delete) operations.

The intended use-case is interactive exploration and scripting.

## Demo

The first argument to `sql-cli` is a SQLite database. In this demo, we'll use
the [Chinook media database][chinook].

```sh
sql-cli chinook.db
```

```
usage: sql-cli [-h]
               {Album,Artist,Customer,Employee,Genre,Invoice,InvoiceLine,Track,MediaType,Playlist,PlaylistTrack}
               ...
sql-cli: error: the following arguments are required: table
```

As seen above, `sql-cli` generates one subcommand per table. Each table has a
`get` subcommand:

```sh
sql-cli chinook.db Genre get | head -n 3
```

```
1,Rock
2,Jazz
3,Metal
```

By default, `get` returns all records in the table and outputs CSV. Let's
filter based on the genre's primary key (the `GenreId` column), and print it as
a JSON dictionary:

```sh
sql-cli chinook.db Genre get --format jsonl --GenreId-is 2
```

```json
{"GenreId": 2, "Name": "Jazz"}
```

Take a look at the `--help` for any subcommand for more information!

## Features and Roadmap

This tool is quite incomplete. PRs welcome!

- Data formats
  - Get
    - [x] CSV
    - [x] JSONL
    - [x] TSV
- Operations
  - [x] Get
    - [x] Filter on field equality
    - [x] Filter on field inequality
  - [ ] Put
  - [ ] Delete
- Database support
  - [x] SQLite
  - [ ] PostgreSQL
  - [ ] Others?

## How it Works

sql-cli uses SQLAlchemy's reflection mechanism to generate Python objects that
represent the database's schema. It then generates argument parsers based on
this schema, and has generic CRUD operations that consume the results of those
parsers.

## Installation

```python3
git clone https://github.com/langston-barrett/sql-cli
cd sql-cli
pip install .
```

## Development

Optionally create a virtual environment:

```sh
virtualenv venv
source venv/bin/activate
```

Install dependencies:

```sh
pip install -r dev-requirements.txt
pip install -r requirements.txt
```

After making changes, format with `black` and type-check with Mypy:
```sh
black *.py
mypy *.py
```

[chinook]: https://github.com/lerocha/chinook-database
