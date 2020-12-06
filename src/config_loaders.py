import json
from abc import ABC, abstractmethod
from typing import Any, Dict, Final

import toml
import yaml
from path import Path

from .utils.misc import list_to_nested_dicts, merge_nested_dicts


class IConfigLoader(ABC):
    def __init__(self, workdir: Path):
        self._workdir: Final = workdir.abspath()

    @abstractmethod
    def load(self) -> Dict[str, Any]:
        ...


class HugoConfigLoader(IConfigLoader):
    FILE_EXTS = [".toml", ".yaml", ".yml", ".json"]

    def _load_file(self, file: Path) -> Dict[Any, Any]:
        if file.ext in [
            ".toml",
        ]:
            content = dict(toml.loads(file.read_text()))
        elif file.ext in [".yaml", ".yml"]:
            content = yaml.safe_load(file.read_text()) or dict()
        elif file.ext in [
            ".json",
        ]:
            content = dict(json.loads(file.read_text()))

        return content

    def load(self) -> Dict[Any, Any]:
        # Search One Config File
        for ext in self.FILE_EXTS:
            if (file := self._workdir.joinpath(f"config{ext}")).exists():
                return self._load_file(file)
        else:
            # Recursive Search
            config: Dict[Any, Any] = dict()
            for file in self._workdir.joinpath("config").walkfiles():
                if file.ext in self.FILE_EXTS:
                    if file.stem == "config":
                        file_config = self._load_file(file)
                    else:
                        file_config = list_to_nested_dicts(
                            file.stem.split("."), self._load_file(file),
                        )

                    merge_nested_dicts(config, file_config)

        if config:
            return config
        else:
            raise FileNotFoundError(f"No Hugo Configuration Found in {self._workdir}")
