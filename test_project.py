import pytest
import copy
from loader import load_csv
from validators import check_missing_values, check_duplicates
from inference import detect_value_type, infer_column_type, infer_schema

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


# inference

# detect_value_type


@pytest.mark.parametrize(
    "value, expected",
    [
        ("25", "int"),
        ("-10", "int"),
        ("25.5", "float"),
        ("true", "bool"),
        ("FALSE", "bool"),
        ("2025-10-26", "date"),
        ("Alex", "str"),
        ("NaN", "str"),
        ("inf", "str"),
        ("10.0", "float"),
        ("2025-02-30", "str"),
        ("20251026", "int"),
        ("2025-W43-7", "str"),
        ("1_000", "str"),
        (" 25 ", "str"),
        ("1e3", "float"),
        ("", "str"),
    ],
)
def test_detect_value_type(value, expected):
    assert detect_value_type(value) == expected


# infer_column_type
@pytest.mark.parametrize(
    "values, expected",
    [
        (["10", "20", "30"], {"inferred_type": "int", "confidence": 1}),
        (["10", "20.5", "30"], {"inferred_type": "float", "confidence": 1}),
        (
            ["10", "20", "error", "30", "40"],
            {"inferred_type": "int", "confidence": 0.8},
        ),
        (
            ["10", "20.5", "error", "30"],
            {"inferred_type": "unknown", "confidence": 0.75},
        ),
        (["true", "false", "TRUE"], {"inferred_type": "bool", "confidence": 1}),
        (["2025-01-01", "2025-02-01"], {"inferred_type": "date", "confidence": 1}),
        (["Alex", "Bob", "Charlie"], {"inferred_type": "str", "confidence": 1}),
        ([None, "", "   "], {"inferred_type": "unknown", "confidence": 0.0}),
        (["10", None, "20", ""], {"inferred_type": "int", "confidence": 1}),
        (["10", "20", "Alex", "Bob"], {"inferred_type": "unknown", "confidence": 0.5}),
        ([], {"inferred_type": "unknown", "confidence": 0.0}),
    ],
)
def test_infer_column_type(values, expected):
    assert infer_column_type(values) == expected


def test_infer_column_type_no_changes():
    data = ["10", "20.5", "30"]
    copy_data = copy.deepcopy(data)
    infer_column_type(data)
    assert data == copy_data


# infer_schema
@pytest.mark.parametrize(
    "data, expected",
    [
        (
            [
                {"name": "Alex", "age": "25", "salary": "3500.5"},
                {"name": "Bob", "age": "30", "salary": "4200"},
                {"name": "Charlie", "age": "28", "salary": "3900.75"},
            ],
            {
                "name": {"inferred_type": "str", "confidence": 1.0},
                "age": {"inferred_type": "int", "confidence": 1.0},
                "salary": {"inferred_type": "float", "confidence": 1.0},
            },
        ),
        ([], {}),
        (
            [
                {"name": "Alex", "age": "25"},
                {"name": "Bob"},
                {"name": "Charlie", "age": "28"},
            ],
            {
                "name": {"inferred_type": "str", "confidence": 1.0},
                "age": {"inferred_type": "int", "confidence": 1.0},
            },
        ),
        (
            [
                {"name": "Alex", "salary": None},
                {"name": "Bob", "salary": ""},
                {"name": "Charlie", "salary": "   "},
            ],
            {
                "name": {"inferred_type": "str", "confidence": 1.0},
                "salary": {"inferred_type": "unknown", "confidence": 0.0},
            },
        ),
        (
            [
                {"name": "Alex"},
                {"name": "Bob", "age": "25"},
                {"name": "Charlie", "age": "30", "city": "Moscow"},
            ],
            {
                "name": {"inferred_type": "str", "confidence": 1.0},
                "age": {"inferred_type": "int", "confidence": 1.0},
                "city": {"inferred_type": "str", "confidence": 1.0},
            },
        ),
        (
            [
                {"name": "Alex", "age": "25"},
                {"age": "30", "name": "Bob"},
                {"name": "Charlie", "age": "28"},
            ],
            {
                "name": {"inferred_type": "str", "confidence": 1.0},
                "age": {"inferred_type": "int", "confidence": 1.0},
            },
        ),
    ],
)
def test_infer_schema(data, expected):
    assert infer_schema(data) == expected


def test_infer_schema_no_changes():
    data = [
        {"name": "Alex", "age": "25", "salary": "3500.5"},
        {"name": "Bob", "age": "30", "salary": "4200"},
        {"name": "Charlie", "age": "28", "salary": "3900.75"},
    ]
    copy_data = copy.deepcopy(data)
    infer_schema(data)
    assert data == copy_data
