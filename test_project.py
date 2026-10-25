import pytest
import copy
from loader import load_csv
from validators import check_missing_values, check_duplicates

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

# check_missing_values


def test_check_missing_values_no_changes():
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


# check_duplicates


def test_check_duplicates_values_no_changes():
    data = [
        {"id": "1", "name": "Ivan"},
        {"id": "1", "name": "Ivan"},
        {"id": "1", "name": "Ivan"},
        {"id": "2", "name": "Maria"},
        {"id": "3", "name": "Alex"},
        {"id": "3", "name": "Alex"},
    ]
    copy_data = copy.deepcopy(data)
    check_duplicates(data)
    assert data == copy_data


def test_check_duplicates_no_duplicates():
    data = [{"id": "1", "name": "Ivan"}, {"id": "2", "name": "Maria"}]
    assert check_duplicates(data) == {"count": 0, "locations": []}


def test_check_duplicates_empty_data():
    data = []
    assert check_duplicates(data) == {"count": 0, "locations": []}


def test_check_duplicates_none_values():
    data = [
        {"id": "1", "name": None},
        {"id": "2", "name": "Maria"},
        {"id": "1", "name": None},
    ]
    assert check_duplicates(data) == {
        "count": 1,
        "locations": [{"row": 3, "column": None}],
    }


def test_check_duplicates_similar_values_different_keys():
    data = [{"id": "1", "name": "Alex"}, {"id": "Alex", "name": "1"}]
    assert check_duplicates(data) == {"count": 0, "locations": []}


def test_check_duplicates_exist_duplicates():
    data = [
        {"id": "1", "name": "Ivan"},
        {"id": "1", "name": "Ivan"},
        {"id": "1", "name": "Ivan"},
        {"id": "2", "name": "Maria"},
        {"id": "3", "name": "Alex"},
        {"id": "3", "name": "Alex"},
    ]
    assert check_duplicates(data) == {
        "count": 3,
        "locations": [
            {"row": 2, "column": None},
            {"row": 3, "column": None},
            {"row": 6, "column": None},
        ],
    }


def test_check_duplicates_exist_duplicates_different_order():
    data = [
        {"id": "1", "name": "Ivan"},
        {"id": "1", "name": "Ivan"},
        {"name": "Ivan", "id": "1"},
        {"name": "Maria", "id": "2"},
        {"id": "3", "name": "Alex"},
        {"name": "Alex", "id": "3"},
    ]
    assert check_duplicates(data) == {
        "count": 3,
        "locations": [
            {"row": 2, "column": None},
            {"row": 3, "column": None},
            {"row": 6, "column": None},
        ],
    }
