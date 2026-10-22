import pytest
from loader import load_csv

# loader.py tests


def test_loader_valid_csv(tmp_path):
    csv_file = tmp_path / "test.csv"

    csv_file.write_text("id,name\n1,Alex\n2,Maria\n", encoding="utf-8")

    result = load_csv(str(csv_file))

    assert len(result) == 2
    assert result[0]["name"] == "Alex"
    assert result[1]["id"] == "2"


def test_loader_empty_csv(tmp_path):
    csv_file = tmp_path / "test.csv"

    csv_file.write_text("", encoding="utf-8")

    result = load_csv(str(csv_file))

    assert result == []


def test_loader_missing_csv(tmp_path):
    csv_file = tmp_path / "test.csv"
    with pytest.raises(FileNotFoundError):
        load_csv(str(csv_file))
