import json
import logging
from pathlib import Path
import re
from dotenv import load_dotenv
import yaml


class ExampleClass:
    EXAMPLE_NUM_RE = re.compile(r"ex[0-9]{2}")

    def __init__(self,
                 config: str | Path | dict) -> None:
        load_dotenv(dotenv_path=".env.shared")
        load_dotenv(dotenv_path=".env", override=True)

        example_dir = self.__class__.__module__.split(".")[-2]
        self._example_num = self.EXAMPLE_NUM_RE.match(example_dir).group()

        self._name = (f"{Path(__file__).parent.parent.name}"
                      f".{example_dir}"
                      f".{self.__class__.__name__}")

        self._l = logging.getLogger(f"{self._name}")
        self._l.info(f"Initializing example '{self._example_num}'")


        if isinstance(config, (str, Path)):
            config_path = Path(config).resolve().absolute()
            if config_path.suffix == ".json":
                with open(config_path, mode="r", encoding="utf-8") as file:
                    config = json.load(file)
            elif config_path.suffix == ".yaml":
                with open(config_path, mode="r", encoding="utf-8") as file:
                    config = yaml.safe_load(file)
            else:
                raise ValueError(f"Invalid config file type: {config_path}")

        if self._example_num not in config:
            raise ValueError(f"Example number key '{self._example_num}' not found in config")

        self._config = config[self._example_num]
