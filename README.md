# DataGuard

DataGuard is a lightweight command-line tool for analyzing the quality of CSV datasets. Built with Python's standard library, it identifies missing values, duplicate records, and type anomalies, and generates structured reports for further investigation.

The application supports summary and detailed console reports, as well as JSON export for integration with other tools and workflows.

## Overview

Data quality is an important part of reliable analytics and data processing.

When working with CSV files from external sources, data quality cannot always be guaranteed. Files may contain missing values, duplicate rows, or inconsistent data types that can affect downstream processing.

These issues may lead to unreliable analysis, incorrect conclusions, and unexpected errors in analytical systems.

DataGuard helps identify potential problems before data is loaded into other applications.

Instead of manually inspecting CSV files, users can run automated validation checks and review the results in a structured report.

The project is intended for Python developers, data analysts, and data engineers who need a simple way to perform preliminary data quality checks.

## Features

### Missing Value Detection

Detects missing values, including empty strings, whitespace-only strings, and absent values represented as `None`.

The report identifies affected rows and columns.

### Duplicate Row Detection

Identifies repeated rows whose values match an earlier row.

The first occurrence of each distinct row is excluded from the duplicate count.

### Type Inference

Analyzes non-missing values in each column to infer the most likely data type.

Supported types include:

- `int`
- `float`
- `bool`
- `date`
- `str`

A column is assigned a type when at least 80% of its non-missing values match the dominant type.

Otherwise, the inferred type is classified as `unknown`.

Integer values are treated as compatible with floating-point values during type inference.

### Type Anomaly Detection

Compares individual values with their column's inferred type.

Values incompatible with the expected type are flagged as potential anomalies.

Missing values and columns classified as `unknown` are excluded from this check.

### Summary and Verbose Reports

The summary report provides:

- Total number of analyzed rows
- Total number of columns
- Total number of detected issues
- Issue counts by category

The verbose report includes the summary and additional information about issue locations.

### JSON Export

Exports the complete structured analysis report to a JSON file.

The exported report contains dataset statistics, inferred column types, validation results, issue counts, and affected locations.

JSON export is independent of the selected console reporting mode.

## Project Structure

DataGuard uses a modular architecture that separates data loading, schema inference, validation, and reporting.

```text
dataguard/
├── .github/
│   └── workflows/
│       └── ci.yml
├── tests/
├── project.py
├── loader.py
├── inference.py
├── validators.py
├── reporting.py
├── requirements-dev.txt
└── README.md
```

| File / Directory | Description |
|---|---|
| `project.py` | Main entry point, command-line argument handling, and workflow coordination |
| `loader.py` | CSV loading and structural validation |
| `inference.py` | Value type detection, schema inference, and type compatibility checks |
| `validators.py` | Missing-value, duplicate-row, and type-anomaly detection |
| `reporting.py` | Structured report generation, console formatting, and JSON export |
| `tests/` | Automated tests using pytest |
| `.github/workflows/ci.yml` | GitHub Actions continuous integration workflow |
| `requirements-dev.txt` | Development dependencies |

The modular design makes individual components easier to test and maintain.

It also allows the core validation functionality to be reused without relying on the command-line interface.

## Installation

### Requirements

- Python 3.14 (tested version)
- Git (for cloning the repository)

DataGuard uses Python's standard library for its core functionality, so no additional runtime packages are required.

### Clone the Repository

```bash
git clone https://github.com/Holly-Soul/dataguard.git
cd dataguard
```

### Create a Virtual Environment (Optional)

```bash
python -m venv .venv
```

Activate the environment on Windows:

```powershell
.venv\Scripts\Activate.ps1
```

Or on Linux/macOS:

```bash
source .venv/bin/activate
```

### Install Development Dependencies

To run tests and code quality checks, install the optional development dependencies:

```bash
python -m pip install -r requirements-dev.txt
```

These dependencies include `pytest` and `ruff`.

## Usage

DataGuard accepts a path to a CSV file and optional command-line arguments.

### Basic Analysis

```bash
python project.py yourCSV.csv
```

Runs the available validation checks and displays a summary report.

Example output:

```text
========================================
            DATAGUARD REPORT
========================================

Rows analyzed:             100
Columns analyzed:            5
Total issues:               12

----------------------------------------
             ISSUES SUMMARY
----------------------------------------

Missing values:              6
Duplicate rows:              4
Type anomalies:              2
```

*The values above are illustrative.*

### Verbose Report

```bash
python project.py yourCSV.csv --verbose
```

Or use the shorter option:

```bash
python project.py yourCSV.csv -v
```

The verbose report displays the same summary information and adds the locations of detected issues.

For example, a missing value may be reported as:

```text
Row 5  |  Column: email
```

### JSON Export

```bash
python project.py yourCSV.csv --json report.json
```

Saves the complete analysis report to `report.json`.

The application also displays a summary report in the terminal.

To export JSON and display detailed results simultaneously:

```bash
python project.py yourCSV.csv --verbose --json report.json
```

The `--verbose` option affects only the console output. The JSON file always contains the complete structured report.

### Command-Line Help

```bash
python project.py --help
```

Displays the available arguments and their descriptions.

## How It Works

DataGuard follows a four-stage data processing workflow.

### 1. CSV Loading

The application receives a CSV file path through its command-line interface.

The `loader.py` module reads the file using Python's built-in `csv.DictReader` and stores the records as a list of dictionaries.

During loading, DataGuard checks for duplicate column names, empty datasets, and rows containing more values than the CSV header defines.

CSV files are expected to use UTF-8 encoding.

### 2. Schema Inference

The `inference.py` module analyzes the values in each column to determine their most likely types.

Missing values are excluded from this process.

A column receives an inferred type when at least 80% of its non-missing values match the dominant type. Otherwise, its type is classified as `unknown`.

When floating-point values are present, integer values are treated as floating-point values for determining the dominant type.

### 3. Data Validation

After schema inference, DataGuard performs three independent checks:

- Missing-value detection
- Duplicate-row detection
- Type-anomaly detection

Each validator returns a structured dictionary containing an issue count and a list of affected locations.

### 4. Report Generation

The `reporting.py` module combines dataset statistics, the inferred schema, and validation results into a single report.

The application displays either a summary or a detailed report in the terminal.

When the `--json` option is provided, the complete report is also saved to a JSON file.

## Design Decisions

### Modular Architecture

DataGuard separates CSV loading, schema inference, validation, reporting, and command-line interaction into independent modules.

This makes the code easier to understand, test, and maintain.

Individual validation functions can be tested without executing the complete CLI workflow.

The modular architecture also provides a foundation for future integration into larger data-processing systems.

### Standard Library First

DataGuard uses Python's standard library for its core functionality.

The `csv` module handles file parsing, `argparse` provides the command-line interface, and `json` supports structured report export.

Avoiding additional runtime dependencies keeps installation simple and reduces project complexity.

External packages such as `pytest` and `ruff` are used only during development and testing.

### Single CSV Load

The CSV file is loaded into memory once.

The resulting data structure is then reused for schema inference and all validation checks.

This avoids repeatedly reading the same file from disk and keeps the processing workflow straightforward.

However, storing the complete dataset in memory limits the application's suitability for very large files.

### Structured Validation Results

Each validator returns a dictionary containing an issue count and a list of affected locations.

Using a consistent result structure simplifies report generation and allows validators to be combined without tightly coupling them to the reporting module.

### Command-Line Interface

A CLI was selected as the primary interface because it provides a simple way to analyze files without requiring a graphical interface or web server.

It also makes DataGuard suitable for manual data checks and potential integration into automated workflows.

### Reusability

The main analysis logic is exposed through the `analyze_csv()` function, which returns a structured Python dictionary.

This separates the core analysis process from terminal output and provides a foundation for future integration into other Python applications.

## Testing & Continuous Integration

DataGuard uses `pytest` for automated testing and `ruff` for linting and formatting checks.

The test suite verifies the behavior of individual components, including CSV loading, type inference, data validation, and report generation.

### Run Tests

```bash
python -m pytest -q
```

### Check Code Quality

```bash
ruff check .
```

### Check Formatting

```bash
ruff format --check .
```

### Continuous Integration

The project uses GitHub Actions for continuous integration.

The CI workflow runs automatically on pushes and pull requests.

It performs the following operations:

1. Checks out the repository.
2. Sets up Python.
3. Installs development dependencies.
4. Runs Ruff linting.
5. Checks code formatting.
6. Executes the pytest test suite.

The `main` branch is protected by a GitHub ruleset that requires the `quality-check` job to pass before changes can be merged.

This helps detect regressions and maintain consistent code quality.

## Limitations & Future Improvements

DataGuard is a lightweight data quality analyzer rather than a complete data validation framework.

### Current Limitations

- **CSV-only input:** The application currently supports CSV files but does not process Excel, Parquet, or database tables.
- **UTF-8 encoding:** CSV files are expected to use UTF-8 encoding.
- **In-memory processing:** The entire dataset is loaded into memory, which may become inefficient for large files.
- **Heuristic type inference:** Column types are inferred from their values rather than from an explicitly defined schema.
- **Limited type validation:** Columns inferred as `unknown` are excluded from type-anomaly checks. String columns accept values regardless of their individually detected types.
- **Fixed validation rules:** Users cannot currently define custom validation rules or configure the type-inference threshold through the CLI.

### Future Improvements

Potential improvements include:

- Configurable validation rules and explicit schemas
- Additional checks, such as value ranges and uniqueness constraints
- Streaming or chunk-based processing for large datasets
- Support for additional file formats and database sources
- Integration with Pandas for advanced data analysis
- Integration into larger data-processing and decision-support systems, including DeciNexus

These improvements are potential future developments and are not part of the current implementation.

## License

A software license has not yet been selected for this project.

Licensing information will be updated when a license is added to the repository.
