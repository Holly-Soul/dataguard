import pytest
import copy
from loader import load_csv
from validators import check_missing_values, check_duplicates, check_type_anomalies
from inference import (
    detect_value_type,
    infer_column_type,
    infer_schema,
    is_type_compatible,
)
from reporting import build_report, format_summary
from project import analyze_csv


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


# check_type_anomalies
@pytest.mark.parametrize(
    "data, schema, expected",
    [
        # 1. Одна аномалия
        (
            [
                {"name": "Alex", "age": "25"},
                {"name": "Bob", "age": "30"},
                {"name": "Charlie", "age": "unknown"},
                {"name": "David", "age": "35"},
            ],
            {
                "name": {"inferred_type": "str", "confidence": 1.0},
                "age": {"inferred_type": "int", "confidence": 0.75},
            },
            {
                "count": 1,
                "locations": [{"row": 3, "column": "age"}],
            },
        ),
        # 2. Несколько аномалий
        (
            [
                {"age": "25", "salary": "3500.5"},
                {"age": "wrong", "salary": "4200"},
                {"age": "30", "salary": "error"},
                {"age": "invalid", "salary": "5000.75"},
            ],
            {
                "age": {"inferred_type": "int", "confidence": 0.5},
                "salary": {"inferred_type": "float", "confidence": 0.75},
            },
            {
                "count": 3,
                "locations": [
                    {"row": 2, "column": "age"},
                    {"row": 3, "column": "salary"},
                    {"row": 4, "column": "age"},
                ],
            },
        ),
        # 3. Нет аномалий
        (
            [
                {"name": "Alex", "age": "25"},
                {"name": "Bob", "age": "30"},
                {"name": "Charlie", "age": "35"},
            ],
            {
                "name": {"inferred_type": "str", "confidence": 1.0},
                "age": {"inferred_type": "int", "confidence": 1.0},
            },
            {
                "count": 0,
                "locations": [],
            },
        ),
        # 4. Пропущенные значения игнорируются
        (
            [
                {"age": "25"},
                {"age": None},
                {"age": ""},
                {"age": "   "},
                {"age": "30"},
            ],
            {
                "age": {"inferred_type": "int", "confidence": 1.0},
            },
            {
                "count": 0,
                "locations": [],
            },
        ),
        # 5. Столбец с типом unknown пропускается
        (
            [
                {"age": "25"},
                {"age": "unknown"},
                {"age": "30.5"},
                {"age": "invalid"},
            ],
            {
                "age": {"inferred_type": "unknown", "confidence": 0.5},
            },
            {
                "count": 0,
                "locations": [],
            },
        ),
        # 6. int совместим с float
        (
            [
                {"salary": "3500"},
                {"salary": "4200.5"},
                {"salary": "3900"},
                {"salary": "5000.75"},
            ],
            {
                "salary": {"inferred_type": "float", "confidence": 1.0},
            },
            {
                "count": 0,
                "locations": [],
            },
        ),
        # 7. Отсутствующий ключ в строке
        (
            [
                {"name": "Alex", "age": "25"},
                {"name": "Bob"},
                {"name": "Charlie", "age": "invalid"},
                {"name": "David", "age": "30"},
            ],
            {
                "name": {"inferred_type": "str", "confidence": 1.0},
                "age": {"inferred_type": "int", "confidence": 0.75},
            },
            {
                "count": 1,
                "locations": [
                    {"row": 3, "column": "age"},
                ],
            },
        ),
    ],
)
def test_check_type_anomalies(data, schema, expected):
    assert check_type_anomalies(data, schema) == expected


def test_check_type_anomalies_no_changes_in_data():
    data = [
        {"age": "25", "salary": "3500.5"},
        {"age": "wrong", "salary": "4200"},
        {"age": "30", "salary": "error"},
        {"age": "invalid", "salary": "5000.75"},
    ]
    schema = {
        "age": {"inferred_type": "int", "confidence": 0.5},
        "salary": {"inferred_type": "float", "confidence": 0.75},
    }
    copy_data = copy.deepcopy(data)
    check_type_anomalies(data, schema)
    assert data == copy_data


def test_check_type_anomalies_no_changes_in_schema():
    data = [
        {"age": "25", "salary": "3500.5"},
        {"age": "wrong", "salary": "4200"},
        {"age": "30", "salary": "error"},
        {"age": "invalid", "salary": "5000.75"},
    ]
    schema = {
        "age": {"inferred_type": "int", "confidence": 0.5},
        "salary": {"inferred_type": "float", "confidence": 0.75},
    }
    copy_schema = copy.deepcopy(schema)
    check_type_anomalies(data, schema)
    assert schema == copy_schema


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


# is_type_compatible
@pytest.mark.parametrize(
    "expected_type, actual_type, expected",
    [
        ("int", "int", True),
        ("int", "float", False),
        ("float", "int", True),
        ("float", "float", True),
        ("float", "str", False),
        ("bool", "bool", True),
        ("bool", "int", False),
        ("date", "date", True),
        ("date", "str", False),
        ("str", "int", True),
        ("str", "date", True),
        ("unknown", "int", False),
    ],
)
def test_is_type_compatible(expected_type, actual_type, expected):
    assert is_type_compatible(expected_type, actual_type) == expected


# reporting test - build_report,format_summary
@pytest.mark.parametrize(
    "data, schema, checks, expected",
    [
        pytest.param(
            # 1. Обычный отчёт с несколькими ошибками
            [
                {"name": "Alex", "age": "25"},
                {"name": "Maria", "age": ""},
                {"name": "John", "age": "wrong"},
            ],
            {
                "name": {"inferred_type": "str", "confidence": 1.0},
                "age": {"inferred_type": "int", "confidence": 0.5},
            },
            {
                "missing_values": {
                    "count": 1,
                    "locations": [{"row": 2, "column": "age"}],
                },
                "duplicates": {
                    "count": 0,
                    "locations": [],
                },
                "type_anomalies": {
                    "count": 1,
                    "locations": [{"row": 3, "column": "age"}],
                },
            },
            {
                "summary": {
                    "total_rows": 3,
                    "total_columns": 2,
                    "total_issues": 2,
                },
                "schema": {
                    "name": {"inferred_type": "str", "confidence": 1.0},
                    "age": {"inferred_type": "int", "confidence": 0.5},
                },
                "checks": {
                    "missing_values": {
                        "count": 1,
                        "locations": [{"row": 2, "column": "age"}],
                    },
                    "duplicates": {
                        "count": 0,
                        "locations": [],
                    },
                    "type_anomalies": {
                        "count": 1,
                        "locations": [{"row": 3, "column": "age"}],
                    },
                },
            },
            id="standard-report",
        ),
        pytest.param(
            # 2. Данные без ошибок
            [
                {"id": "1", "name": "Alex"},
                {"id": "2", "name": "Maria"},
            ],
            {
                "id": {"inferred_type": "int", "confidence": 1.0},
                "name": {"inferred_type": "str", "confidence": 1.0},
            },
            {
                "missing_values": {"count": 0, "locations": []},
                "duplicates": {"count": 0, "locations": []},
                "type_anomalies": {"count": 0, "locations": []},
            },
            {
                "summary": {
                    "total_rows": 2,
                    "total_columns": 2,
                    "total_issues": 0,
                },
                "schema": {
                    "id": {"inferred_type": "int", "confidence": 1.0},
                    "name": {"inferred_type": "str", "confidence": 1.0},
                },
                "checks": {
                    "missing_values": {"count": 0, "locations": []},
                    "duplicates": {"count": 0, "locations": []},
                    "type_anomalies": {"count": 0, "locations": []},
                },
            },
            id="no-issues",
        ),
        pytest.param(
            # 3. Полностью пустой набор данных
            [],
            {},
            {},
            {
                "summary": {
                    "total_rows": 0,
                    "total_columns": 0,
                    "total_issues": 0,
                },
                "schema": {},
                "checks": {},
            },
            id="empty-data",
        ),
        pytest.param(
            # 4. Данные есть, но проверки не выполнялись
            [
                {"id": "1", "name": "Alex"},
                {"id": "2", "name": "Maria"},
            ],
            {
                "id": {"inferred_type": "int", "confidence": 1.0},
                "name": {"inferred_type": "str", "confidence": 1.0},
            },
            {},
            {
                "summary": {
                    "total_rows": 2,
                    "total_columns": 2,
                    "total_issues": 0,
                },
                "schema": {
                    "id": {"inferred_type": "int", "confidence": 1.0},
                    "name": {"inferred_type": "str", "confidence": 1.0},
                },
                "checks": {},
            },
            id="no-checks",
        ),
        pytest.param(
            # 5. Несколько типов ошибок одновременно
            [
                {"id": "1", "age": "25"},
                {"id": "1", "age": "25"},
                {"id": "2", "age": ""},
                {"id": "3", "age": "wrong"},
            ],
            {
                "id": {"inferred_type": "int", "confidence": 1.0},
                "age": {"inferred_type": "int", "confidence": 0.75},
            },
            {
                "missing_values": {
                    "count": 1,
                    "locations": [{"row": 3, "column": "age"}],
                },
                "duplicates": {
                    "count": 1,
                    "locations": [{"row": 2, "column": None}],
                },
                "type_anomalies": {
                    "count": 1,
                    "locations": [{"row": 4, "column": "age"}],
                },
            },
            {
                "summary": {
                    "total_rows": 4,
                    "total_columns": 2,
                    "total_issues": 3,
                },
                "schema": {
                    "id": {"inferred_type": "int", "confidence": 1.0},
                    "age": {"inferred_type": "int", "confidence": 0.75},
                },
                "checks": {
                    "missing_values": {
                        "count": 1,
                        "locations": [{"row": 3, "column": "age"}],
                    },
                    "duplicates": {
                        "count": 1,
                        "locations": [{"row": 2, "column": None}],
                    },
                    "type_anomalies": {
                        "count": 1,
                        "locations": [{"row": 4, "column": "age"}],
                    },
                },
            },
            id="multiple-issue-types",
        ),
        pytest.param(
            # 6. Дополнительный валидатор
            [
                {"id": "1"},
                {"id": "2"},
            ],
            {
                "id": {"inferred_type": "int", "confidence": 1.0},
            },
            {
                "missing_values": {"count": 0, "locations": []},
                "custom_validator": {
                    "count": 5,
                    "locations": [],
                },
            },
            {
                "summary": {
                    "total_rows": 2,
                    "total_columns": 1,
                    "total_issues": 5,
                },
                "schema": {
                    "id": {"inferred_type": "int", "confidence": 1.0},
                },
                "checks": {
                    "missing_values": {"count": 0, "locations": []},
                    "custom_validator": {
                        "count": 5,
                        "locations": [],
                    },
                },
            },
            id="custom-validator",
        ),
    ],
)
def test_build_report(data, schema, checks, expected):
    result = build_report(data, schema, checks)
    assert result == expected


def test_build_report_no_changes_in_data():
    data = [
        {"id": "1", "age": "25"},
        {"id": "2", "age": ""},
    ]

    schema = {
        "id": {"inferred_type": "int", "confidence": 1.0},
        "age": {"inferred_type": "int", "confidence": 1.0},
    }

    checks = {
        "missing_values": {
            "count": 1,
            "locations": [{"row": 2, "column": "age"}],
        },
    }

    original_data = copy.deepcopy(data)

    build_report(data, schema, checks)

    assert data == original_data


def test_build_report_no_changes_in_schema():
    data = [
        {"id": "1", "age": "25"},
        {"id": "2", "age": ""},
    ]

    schema = {
        "id": {"inferred_type": "int", "confidence": 1.0},
        "age": {"inferred_type": "int", "confidence": 1.0},
    }

    checks = {
        "missing_values": {
            "count": 1,
            "locations": [{"row": 2, "column": "age"}],
        },
    }

    original_schema = copy.deepcopy(schema)

    build_report(data, schema, checks)

    assert schema == original_schema


def test_build_report_no_changes_in_checks():
    data = [
        {"id": "1", "age": "25"},
        {"id": "2", "age": ""},
    ]

    schema = {
        "id": {"inferred_type": "int", "confidence": 1.0},
        "age": {"inferred_type": "int", "confidence": 1.0},
    }

    checks = {
        "missing_values": {
            "count": 1,
            "locations": [{"row": 2, "column": "age"}],
        },
    }

    original_checks = copy.deepcopy(checks)

    build_report(data, schema, checks)

    assert checks == original_checks


def test_format_summary_standard():
    report = {
        "summary": {
            "total_rows": 100,
            "total_columns": 5,
            "total_issues": 12,
        },
        "checks": {
            "missing_values": {"count": 5, "locations": []},
            "duplicates": {"count": 3, "locations": []},
            "type_anomalies": {"count": 4, "locations": []},
        },
    }

    result = format_summary(report)

    expected = (
        f"{'=' * 40}\n"
        f"{'DATAGUARD REPORT':^40}\n"
        f"{'=' * 40}\n\n"
        f"{'Rows analyzed:':<22}{100:>6}\n"
        f"{'Columns analyzed:':<22}{5:>6}\n"
        f"{'Total issues:':<22}{12:>6}\n\n"
        f"{'-' * 40}\n"
        f"{'ISSUES SUMMARY':^40}\n"
        f"{'-' * 40}\n\n"
        f"{'Missing values:':<22}{5:>6}\n"
        f"{'Duplicate rows:':<22}{3:>6}\n"
        f"{'Type anomalies:':<22}{4:>6}\n"
    )

    assert result == expected
    assert isinstance(result, str)


def test_format_summary_no_issues():
    report = {
        "summary": {
            "total_rows": 25,
            "total_columns": 3,
            "total_issues": 0,
        },
        "checks": {
            "missing_values": {"count": 0, "locations": []},
            "duplicates": {"count": 0, "locations": []},
            "type_anomalies": {"count": 0, "locations": []},
        },
    }

    result = format_summary(report)

    assert f"{'Rows analyzed:':<22}{25:>6}" in result
    assert f"{'Columns analyzed:':<22}{3:>6}" in result
    assert f"{'Total issues:':<22}{0:>6}" in result
    assert f"{'Missing values:':<22}{0:>6}" in result
    assert f"{'Duplicate rows:':<22}{0:>6}" in result
    assert f"{'Type anomalies:':<22}{0:>6}" in result


def test_format_summary_empty_data():
    report = {
        "summary": {
            "total_rows": 0,
            "total_columns": 0,
            "total_issues": 0,
        },
        "checks": {
            "missing_values": {"count": 0, "locations": []},
            "duplicates": {"count": 0, "locations": []},
            "type_anomalies": {"count": 0, "locations": []},
        },
    }

    result = format_summary(report)

    assert result.count("0") == 6
    assert "DATAGUARD REPORT" in result
    assert "ISSUES SUMMARY" in result


def test_format_summary_no_mutation():
    report = {
        "summary": {
            "total_rows": 10,
            "total_columns": 2,
            "total_issues": 2,
        },
        "schema": {
            "id": {"inferred_type": "int", "confidence": 1.0},
            "age": {"inferred_type": "int", "confidence": 0.9},
        },
        "checks": {
            "missing_values": {
                "count": 1,
                "locations": [{"row": 3, "column": "age"}],
            },
            "duplicates": {
                "count": 0,
                "locations": [],
            },
            "type_anomalies": {
                "count": 1,
                "locations": [{"row": 7, "column": "age"}],
            },
        },
    }

    original = copy.deepcopy(report)

    format_summary(report)

    assert report == original


# project.py integration tests
def test_analyze_csv_valid(tmp_path):
    csv_file = tmp_path / "valid.csv"

    csv_file.write_text(
        "id,name,age\n" "1,Alex,25\n" "2,Maria,30\n" "3,John,35\n",
        encoding="utf-8",
    )

    report = analyze_csv(str(csv_file))

    assert report["summary"] == {
        "total_rows": 3,
        "total_columns": 3,
        "total_issues": 0,
    }

    assert report["schema"]["age"]["inferred_type"] == "int"

    assert report["checks"]["missing_values"]["count"] == 0
    assert report["checks"]["duplicates"]["count"] == 0
    assert report["checks"]["type_anomalies"]["count"] == 0


def test_analyze_csv_issues(tmp_path):
    csv_file = tmp_path / "issues.csv"

    csv_file.write_text(
        "id,name,age\n"
        "1,Alex,25\n"
        "2,Maria,30\n"
        "3,John,35\n"
        "4,Anna,40\n"
        "5,Peter,45\n"
        "6,Kate,50\n"
        "7,Tom,55\n"
        "8,Emma,60\n"
        "9,Max,65\n"
        "10,Bob,wrong\n"
        "11,Lucy,\n",
        encoding="utf-8",
    )

    report = analyze_csv(str(csv_file))

    assert report["summary"]["total_rows"] == 11
    assert report["summary"]["total_columns"] == 3

    assert report["schema"]["age"]["inferred_type"] == "int"
    assert report["schema"]["age"]["confidence"] == 0.9

    assert report["checks"]["missing_values"] == {
        "count": 1,
        "locations": [{"row": 11, "column": "age"}],
    }

    assert report["checks"]["type_anomalies"] == {
        "count": 1,
        "locations": [{"row": 10, "column": "age"}],
    }

    assert report["checks"]["duplicates"] == {
        "count": 0,
        "locations": [],
    }

    assert report["summary"]["total_issues"] == 2


def test_analyze_csv_duplicates(tmp_path):
    csv_file = tmp_path / "duplicates.csv"

    csv_file.write_text(
        "id,name,age\n"
        "1,Alex,25\n"
        "2,Maria,30\n"
        "1,Alex,25\n"
        "3,John,35\n"
        "2,Maria,30\n",
        encoding="utf-8",
    )

    report = analyze_csv(str(csv_file))

    assert report["checks"]["duplicates"] == {
        "count": 2,
        "locations": [
            {"row": 3, "column": None},
            {"row": 5, "column": None},
        ],
    }

    assert report["summary"]["total_issues"] == 2


def test_analyze_csv_empty(tmp_path):
    csv_file = tmp_path / "empty.csv"

    csv_file.write_text(
        "id,name,age\n",
        encoding="utf-8",
    )

    report = analyze_csv(str(csv_file))

    assert report["summary"] == {
        "total_rows": 0,
        "total_columns": 0,
        "total_issues": 0,
    }

    assert report["schema"] == {}

    assert report["checks"]["missing_values"]["count"] == 0
    assert report["checks"]["duplicates"]["count"] == 0
    assert report["checks"]["type_anomalies"]["count"] == 0


def test_analyze_csv_missing_file(tmp_path):
    missing_file = tmp_path / "nonexistent.csv"

    with pytest.raises(FileNotFoundError):
        analyze_csv(str(missing_file))
