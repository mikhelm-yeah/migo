# MIGO - Arena PLM to Claude Integration

A Python-based tool for querying Arena PLM product data, analyzing BOM structures, detecting variations between SKUs, and validating data integrity.

## Features

- **Product Query**: Retrieve detailed product information from Arena PLM
- **BOM Analysis**: Compare bill of materials across multiple SKUs
- **Variation Detection**: Identify intentional vs. inadvertent differences in product structures
- **Data Validation**: 
  - Detect missing or empty fields
  - Validate syntax and data formatting
  - Verify material specifications
  - Generate quality reports
- **Report Generation**: Tabulated reports with data quality metrics

## Project Structure

```
migo/
├── README.md
├── requirements.txt
├── config.py              # Configuration and credentials
├── arena_client.py        # Arena PLM API client
├── bom_analyzer.py        # BOM comparison and analysis
├── data_validator.py      # Data validation and quality checks
├── report_generator.py    # Report formatting and output
├── claude_integration.py  # Claude API integration
└── main.py               # CLI entry point
```

## Setup

### Prerequisites
- Python 3.10+
- Arena PLM API credentials
- Anthropic Claude API key

### Installation

```bash
pip install -r requirements.txt
```

### Configuration

Create a `.env` file with your credentials:

```
ARENA_API_KEY=your_arena_api_key
ARENA_API_URL=https://api.arenasolutions.com/v1
CLAUDE_API_KEY=your_claude_api_key
```

## Usage

### Query a Single Product

```python
from arena_client import ArenaClient

client = ArenaClient()
product = client.get_product("SKU-12345")
print(product)
```

### Compare Multiple SKUs

```python
from bom_analyzer import BOMAnalyzer

analyzer = BOMAnalyzer()
comparison = analyzer.compare_skus(["SKU-001", "SKU-002", "SKU-003"])
analyzer.generate_variation_report(comparison)
```

### Validate Data Quality

```python
from data_validator import DataValidator

validator = DataValidator()
product = client.get_product("SKU-12345")
validation_report = validator.validate_product(product)
validator.print_report(validation_report)
```

## Key Use Cases

1. **BOM Comparison**: Detect color variations, material changes, or structural differences across product lines
2. **Error Detection**: Automatically flag missing required fields, invalid syntax, or incorrect material specifications
3. **Data Quality Reporting**: Generate executive summaries of data completeness and consistency
4. **Change Auditing**: Track and categorize intentional vs. inadvertent product structure changes

## API Integration

### Arena PLM API
- Queries product data, BOMs, parts, revisions
- Authentication via API key
- Rate limiting and pagination handled

### Claude Integration
- Natural language analysis of BOM changes
- Intelligent summarization of variation reports
- Contextual recommendations for resolving data quality issues

## License

MIT
