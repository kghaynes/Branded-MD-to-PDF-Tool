# Branded PDF Generator

## Overview

This project provides a Python tool (`md_to_pdf.py`) that converts markdown files into professionally branded PDF documents with company headers, footers, and data classification labels.

## Usage

```bash
python3 md_to_pdf.py <input.md> -o <output.pdf> --classification <LEVEL> --config <config.yaml>
```

### Arguments

| Argument | Required | Default | Description |
|---|---|---|---|
| `input` | Yes | — | Path to the input markdown file |
| `-o`, `--output` | No | `<input_stem>.pdf` | Path to the output PDF file |
| `-c`, `--classification` | No | `INTERNAL` | Data classification level |
| `--config` | No | `config.yaml` | Path to YAML configuration file |

### Classification Levels

- `PUBLIC` — Green label
- `INTERNAL` — Yellow label
- `CONFIDENTIAL` — Orange label
- `SECRET` — Red label

## Configuration

Company branding is defined in `config.yaml`:

- `company.name` — Company name displayed in the header
- `company.email` — Contact email displayed in the header
- `company.website` — Website displayed in the header
- `company.logo_path` — Absolute path to a PNG or JPG logo file
- `classifications.<LEVEL>.color` — Hex background color for the classification badge
- `classifications.<LEVEL>.text_color` — Hex text color for the classification badge

## PDF Layout

Each page contains:

- **Header**: Company logo (left), company name/email/website (right-aligned), with a 1pt separator line below
- **Body**: Rendered markdown content
- **Footer**: 1pt separator line above, then classification badge (left), date created (center), "Page X of Y" (right)

## Markdown Support

- Headings (H1-H3)
- Paragraphs
- Lists (ordered and unordered)
- Code blocks
- Tables
- Inline formatting (bold, italic, code)
- YAML frontmatter — extracted as invisible PDF metadata (`title`, `author`, `date`), not rendered in body

## Virtual Environment

This project requires a Python virtual environment. Activate before running:

```bash
source venv/bin/activate   # macOS/Linux
pip install -r requirements.txt
```

### Dependencies

- `reportlab` — PDF generation
- `markdown2` — Markdown to HTML conversion
- `PyYAML` — Configuration loading
- `Pillow` — Logo image handling
- `PyPDF2` — Page count detection

## Key Files

- `md_to_pdf.py` — Main script
- `config.yaml` — Company branding and classification color configuration
- `requirements.txt` — Python dependencies
- `example_doc.md` — Sample markdown file for testing

## Example

```bash
source venv/bin/activate
python3 md_to_pdf.py example_doc.md -o report.pdf --classification CONFIDENTIAL
```

This generates `report.pdf` with CyberCloudAI Consulting LLC branding, an orange CONFIDENTIAL badge in the footer, the current date, and "Page X of Y" pagination.
