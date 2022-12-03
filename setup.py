#!/usr/bin/env python3

from setuptools import find_packages, setup

with open("./README.md") as f:
    long_description = f.read()

with open("./requirements.txt") as f:
    requirements = list(f.read().splitlines())

setup(
    name="sql-cli",
    version="0.0.0",
    license="MIT",
    author="Langston Barrett",
    author_email="langston.barrett@gmail.com",
    description="Dynamically generate CLIs from SQL databases that support CRUD operations",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/langston-barrett/sql-cli",
    project_urls={"Documentation": "https://github.com/langston-barrett/sql-cli"},
    packages=find_packages(),
    platforms="any",
    python_requires=">=3.8",
    install_requires=requirements,
    entry_points={
        "console_scripts": ["sql-cli = sql_cli.cli:main"],
    },
)
