import pytest
import copy
from loader import load_csv
from validators import check_missing_values

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


# validators.py tests


def test_validator_no_changes():
    data = [{"id": "1", "name": "Alex"}, {"id": "2", "name": "Maria"}]
    copy_data = copy.deepcopy(data)
    check_missing_values(data)
    assert data == copy_data


def test_validator_missing_value_no_missing():
    data = [{"id": "1", "name": "Alex"}, {"id": "2", "name": "Maria"}]
    assert check_missing_values(data) == {"count": 0, "locations": []}


def test_validator_missing_value_several_missings():
    data = [
        {"id": "1", "name": ""},
        {"id": "2", "name": "Maria"},
        {"id": "3", "name": None},
        {"id": "4", "name": "", "age": None},
    ]
    assert check_missing_values(data) == {
        "count": 4,
        "locations": [
            {"row": 1, "column": "name"},
            {"row": 3, "column": "name"},
            {"row": 4, "column": "name"},
            {"row": 4, "column": "age"},
        ],
    }


def test_validator_missing_value_empty_data():
    data = []
    assert check_missing_values(data) == {"count": 0, "locations": []}
