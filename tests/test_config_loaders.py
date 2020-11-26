import pytest
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

    def test_one_file_toml(self):
        hugo = HugoConfigLoader(workdir=Path("tests/assets/configs/hugo/one_file_toml"))
        config = hugo.load()

        assert config == self.EXPECTED_CONFIG

    def test_one_file_yaml(self):
        hugo = HugoConfigLoader(workdir=Path("tests/assets/configs/hugo/one_file_yaml"))
        config = hugo.load()

        assert config == self.EXPECTED_CONFIG

    def test_one_file_yml(self):
        hugo = HugoConfigLoader(workdir=Path("tests/assets/configs/hugo/one_file_yml"))
        config = hugo.load()

        assert config == self.EXPECTED_CONFIG

    def test_one_file_json(self):
        hugo = HugoConfigLoader(workdir=Path("tests/assets/configs/hugo/one_file_json"))
        config = hugo.load()

        assert config == self.EXPECTED_CONFIG

    def test_recursive(self):
        hugo = HugoConfigLoader(workdir=Path("tests/assets/configs/hugo/recursive"))
        config = hugo.load()

        assert config == self.EXPECTED_CONFIG

    def test_no_config_file(self):
        hugo = HugoConfigLoader(
            workdir=Path("tests/assets/configs/hugo/no_config_file")
        )

        with pytest.raises(
            FileNotFoundError, match=f"No Hugo Configuration Found in {hugo._workdir}"
        ):
            hugo.load()
