import json

import pytest
import toml
import yaml
from path import Path

from src.config_loaders import HugoConfigLoader


class TestHugoConfigLoader:
    EXPECTED_CONFIG = {
        "content": "Or we\ncan auto\nconvert line breaks\nto save space",
        "json": ["rigid", "better for data interchange"],
        "object": {
            "array": [{"boolean": True}, {"integer": 1}],
            "key": "value",
            "name": {"first": "Goldie", "last": "Mcbride"},
        },
        "paragraph": "Blank lines denote\nparagraph breaks\n",
        "yaml": ["slim and flexible", "better for configuration"],
    }

    def test_one_file_toml(self, tmpdir):
        tmpdir.mkdir("config")
        with open(tmpdir / "config/config.toml", "w+") as file:
            toml.dump(self.EXPECTED_CONFIG, file)

        hugo = HugoConfigLoader(workdir=Path(tmpdir))
        config = hugo.load()

        assert config == self.EXPECTED_CONFIG

    def test_one_file_yaml(self, tmpdir):
        tmpdir.mkdir("config")
        with open(tmpdir / "config/config.yaml", "w+") as file:
            yaml.dump(self.EXPECTED_CONFIG, file)

        hugo = HugoConfigLoader(workdir=Path(tmpdir))
        config = hugo.load()

        assert config == self.EXPECTED_CONFIG

    def test_one_file_yml(self, tmpdir):
        tmpdir.mkdir("config")
        with open(tmpdir / "config/config.yml", "w+") as file:
            yaml.dump(self.EXPECTED_CONFIG, file)

        hugo = HugoConfigLoader(workdir=Path(tmpdir))
        config = hugo.load()

        assert config == self.EXPECTED_CONFIG

    def test_one_file_json(self, tmpdir):
        tmpdir.mkdir("config")
        with open(tmpdir / "config/config.json", "w+") as file:
            json.dump(self.EXPECTED_CONFIG, file)

        hugo = HugoConfigLoader(workdir=Path(tmpdir))
        config = hugo.load()

        assert config == self.EXPECTED_CONFIG

    def test_recursive(self, tmpdir):
        tmpdir = Path(tmpdir)
        (tmpdir / "config").mkdir()
        (tmpdir / "config/config.toml").write_text(
            'json = ["rigid", "better for data interchange"]'
        )
        (tmpdir / "config/foo").mkdir()
        (tmpdir / "config/foo/config.toml").write_text(
            'yaml = ["slim and flexible", "better for configuration"]'
        )
        (tmpdir / "config/foo/object.toml").write_text('key = "value"')
        (tmpdir / "config/foo/bar").mkdir()
        (tmpdir / "config/foo/bar/config.toml").write_text(
            """
content = '''
Or we
can auto
convert line breaks
to save space'''
paragraph = '''
Blank lines denote
paragraph breaks
'''

[[object.array]]
boolean = true

[[object.array]]
integer = 1
"""
        )
        (tmpdir / "config/foo/bar/object.name.toml").write_text(
            'first = "Goldie"\nlast = "Mcbride"'
        )

        hugo = HugoConfigLoader(workdir=Path(tmpdir))
        config = hugo.load()

        assert config == self.EXPECTED_CONFIG

    def test_no_config_file(self, tmpdir):
        tmpdir = Path(tmpdir)
        (tmpdir / "_config.json").write_text("Should be ignored")
        (tmpdir / "cconfig.yaml").write_text("Should be ignored")
        (tmpdir / "Config.toml").write_text("Should be ignored")
        (tmpdir / "foo.bar").write_text("Should be ignored")
        (tmpdir / "config").mkdir()
        (tmpdir / "config/config.txt").write_text("Should be ignored")
        (tmpdir / "config/spam.egg").write_text("Should be ignored")
        (tmpdir / "config/dir").mkdir()
        (tmpdir / "config/dir/barfoo").write_text("Should be ignored")

        hugo = HugoConfigLoader(workdir=Path(tmpdir))

        with pytest.raises(
            FileNotFoundError, match=f"No Hugo Configuration Found in {hugo._workdir}"
        ):
            hugo.load()
