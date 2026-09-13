from argparse import ArgumentParser
import importlib
import logging
import logging.config
import os
from pathlib import Path
import re
from dotenv import load_dotenv
import yaml

from constants import (
    PROJECT_NAME,
)


def main() -> None:
    # Load .env file (if available) variables into os.environ
    this_file_path = Path(__file__).resolve().absolute()
    load_dotenv()

    # We avoid using print statements as much as possible, logging is better to display and control
    with open("logging-config.yaml", "r") as file:
        logging_config = yaml.safe_load(file)
    logging.config.dictConfig(logging_config)
    l = logging.getLogger(PROJECT_NAME)
    l.debug(f"Started {PROJECT_NAME}")

    parser = ArgumentParser(
        prog=PROJECT_NAME,
        description="Examples to learn GenAI",
        allow_abbrev=False
    )

    cmd_args = parser.add_argument_group("command arguments")
    cmd_args.add_argument("-c", "--config-path",
                          type=str,
                          default="config/default.yaml",
                          help="config JSON/YAML path for all examples")
    cmd_args.add_argument("-e", "--example",
                          required=True,
                          type=str,
                          help="example to run")
    args = parser.parse_args()

    # standardize format: ex1=>ex01, 4=>ex04
    example_num = "ex{:0>2}".format(args.example.lower().removeprefix("ex"))

    match_example = re.compile("ex[0-9]{2}")
    example_dirs = [item.name
                    for item in this_file_path.parent.iterdir()
                    if item.is_dir() and match_example.match(item.name) and item.name.lower().startswith(example_num)]

    if not example_dirs:
        raise ValueError(f"Example number '{example_num}' not found, please use correct number")

    example_module = importlib.import_module(f"{example_dirs[0]}")
    getattr(example_module, "MainClass")(config_path=args.config_path).run()

if __name__ == "__main__":
    main()
