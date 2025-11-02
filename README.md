# Credit Card Statement PDF Parser

## Overview

This application extracts financial data from credit card statement PDFs for multiple major issuers. It uses pattern matching and text analysis to identify and extract key data points while maintaining data privacy through local processing. The project provides a Streamlit web interface and a command-line option to parse statements from Chase, Bank of America, Citi, American Express, and Capital One.

## Supported Financial Institutions

- Chase
- Bank of America
- Citi
- American Express
- Capital One

## Extracted Data Points

The parser extracts the following information from each statement:

1. Issuer — Financial institution name (automatically detected)  
2. Cardholder Name — Primary account holder  
3. Card Last 4 Digits — Last four digits of the card number  
4. Statement Period — Billing cycle date range  
5. Payment Due Date — Payment deadline (ISO format)  
6. New Balance — Outstanding balance amount

## Installation

### Prerequisites

- Python 3.8 or higher  
- pip package manager

### Setup

1. Navigate to the project directory:

```bash
cd "e:\Projects\Sure finance"
```

2. (Optional) Create and activate a virtual environment:

Windows (cmd.exe):
```bash
python -m venv .venv
.venv\Scripts\activate
```

macOS/Linux:
```bash
python -m venv .venv
source .venv/bin/activate
```

3. Install required dependencies:

```bash
pip install -r requirements.txt
```

Verify installation:

```bash
python test_imports.py
```

Important notes:
- Do not commit or share real statements publicly. Use the application locally and keep files private.
- The parser uses heuristics and issuer-specific patterns; it may fail on uncommon layouts.

## Quick Start

To run the Streamlit web interface:

```bash
streamlit run app.py
```

The application will launch in the default web browser at http://localhost:8501.

For direct command-line processing:

```bash
python pdf_parser.py path/to/statement.pdf
```

## Usage

1. Open the web interface or use the command line.  
2. Click the upload button to select PDF files (batch upload supported).  
3. The system processes each file and displays extracted data.  
4. Results can be exported in CSV or JSON format.

## Project Structure

- app.py — Streamlit web interface and main application logic  
- pdf_parser.py — Core parsing engine with issuer-specific patterns  
- generate_mock_statements.py — Test data generator  
- requirements.txt — Python dependencies  
- test_imports.py — Package verification utility  
- .gitignore — Version control exclusions  
- README.md — Documentation

## Technical Architecture

### Processing Pipeline

1. PDF Text Extraction: Uses pdfplumber to extract text from each PDF page.  
2. Issuer Detection: Identifies the financial institution through keyword matching.  
3. Pattern Matching: Applies regular expressions to locate specific data points.  
4. Data Validation: Formats and validates extracted information.  
5. Result Compilation: Aggregates data into a structured format (pandas DataFrame).

Recommendations:
- Improve table parsing for transactions using a table-extraction tool (for transaction-level extraction).
- Add issuer-specific tweaks based on sample statements to increase accuracy.

## Key Features

- Local processing: No external servers required.  
- Multi-pattern matching with fallback mechanisms.  
- Issuer-specific extraction logic.  
- Batch processing support.  
- Export options: CSV and JSON.  
- Error handling to continue processing despite individual file failures.

## Privacy and Security

- All processing occurs locally. No data is sent to external servers.  
- Temporary files are deleted immediately after processing.  
- Do not commit real statements to version control. Delete exported files after use.

## Testing

### Mock Statement Generator

Generate test PDFs without using real financial data:

```bash
python generate_mock_statements.py
```

This creates mock statements in a `mock_statements` directory for testing and tuning.

### Performance

- Processing speed: approximately 1–2 seconds per PDF for typical statements.  
- Batch capability: supports processing multiple files concurrently.  
- Memory usage: minimal for typical statement sizes.

## Troubleshooting

Common issues and remedies:

- Package installation fails:
    ```bash
    python -m pip install --upgrade pip
    pip install -r requirements.txt
    ```

- PDF parsing errors:
    - Ensure PDFs are not password-protected.
    - Confirm the PDF contains selectable text (not just images).
    - Check that the issuer is supported.

- Missing data:
    - Some statement formats may vary. Review detailed view for partial extractions and consider adding custom patterns.

## Example Output

The application displays a table of extracted results and supports downloading CSV or JSON exports. Example columns:

| Status | Filename | Issuer | Cardholder Name | Card Last 4 | Statement Period | Payment Due Date | New Balance |

## Dependencies

Key packages included in requirements.txt:

- pdfplumber — PDF text extraction  
- PyMuPDF — Additional PDF processing support  
- streamlit — Web interface framework  
- pandas — Data manipulation  
- python-dateutil — Date parsing  
- reportlab — PDF generation (testing)

## Customization and Extensibility

To add a new issuer:

1. Add issuer name to the ISSUERS list in pdf_parser.py.  
2. Create extraction regex patterns for the new issuer format in extract_fields_from_text().  
3. Add detection keywords to detect_issuer().  
4. Test with sample statements and update the UI as needed.

To add new data points:

1. Add the field to the result dictionary in extract_fields_from_text().  
2. Create regex patterns or rule-based extraction logic.  
3. Update the UI in app.py to display the new field.

## Limitations

- Text-based PDFs only; OCR is not included.  
- Password-protected PDFs are not supported.  
- Accuracy depends on statement layout consistency; non-standard formats may require manual verification.

## Development Notes and Best Practices

- Use type hints and maintain clear function signatures.  
- Separate UI logic from parsing logic.  
- Keep confidential documents out of version control.  
- Delete temporary and exported files after use.

## Future Enhancements

- Add OCR support for image-based PDFs.  
- Extract transaction-level details.  
- Support additional issuers (e.g., Discover, US Bank).  
- Implement machine learning-based extraction for improved accuracy.  
- Add optional database storage for historical tracking.

## License

This project is intended for educational and personal use. Users are responsible for handling financial documents appropriately and in compliance with applicable laws and policies.

## Contact

For technical issues or questions, refer to the inline documentation and code comments. Submit issues via the project's issue tracker.

---
Built with Python, Streamlit, and pdfplumber.
