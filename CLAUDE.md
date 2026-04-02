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

| Element | Notes |
|---|---|
| Headings H1–H6 | Styled with configurable heading color |
| Paragraphs | With bold, italic, inline code, links (text only, URL dropped) |
| Unordered lists | Rendered with bullet points (•) |
| Ordered lists | Rendered with numbers |
| Tables | Header row with grey background, alternating row shading |
| Fenced code blocks | Monospace, whitespace preserved — safe for ASCII art/diagrams |
| Inline code | Courier font |
| Blockquotes | Indented, grey text |
| Horizontal rules | Grey divider line |
| Emoji | Rendered via bundled `NotoEmoji.ttf` (monochrome outline glyphs) |
| YAML frontmatter | Extracted as PDF metadata (`title`, `author`, `date`), not rendered |

## Virtual Environment

This project requires a Python virtual environment. To set up from scratch:

```bash
python3 -m venv venv
source venv/bin/activate   # macOS/Linux
python3 -m ensurepip --upgrade
pip install -r requirements.txt
```

If the venv breaks after a Homebrew Python update (symptom: `ModuleNotFoundError` despite venv being active), delete and recreate it:

```bash
deactivate && rm -rf venv && python3 -m venv venv && source venv/bin/activate && python3 -m ensurepip --upgrade && pip install -r requirements.txt
```

### Dependencies

- `reportlab` — PDF generation
- `markdown2` — Markdown to HTML conversion
- `PyYAML` — Configuration loading
- `Pillow` — Logo image handling
- `pypdf` — Page count detection
- `NotoEmoji.ttf` — Bundled font file (not a pip package) for emoji rendering

## Key Files

- `md_to_pdf.py` — Main script
- `config.yaml` — Company branding and classification color configuration
- `requirements.txt` — Python dependencies
- `NotoEmoji.ttf` — Bundled Google Noto Emoji font (must be in same directory as script)
- `example_doc.md` — Sample markdown file for testing

## Emoji Font

`NotoEmoji.ttf` is bundled in the repo and tracked in git. It is the Google Noto Emoji variable font (monochrome), which ReportLab can render. Apple Color Emoji is NOT compatible with ReportLab. If `NotoEmoji.ttf` is missing, re-download it:

```bash
curl -L -o NotoEmoji.ttf "https://github.com/google/fonts/raw/main/ofl/notoemoji/NotoEmoji%5Bwght%5D.ttf"
```

## Example

```bash
source venv/bin/activate
python3 md_to_pdf.py example_doc.md -o report.pdf --classification CONFIDENTIAL
```

This generates `report.pdf` with company branding, an orange CONFIDENTIAL badge in the footer, the current date, and "Page X of Y" pagination.
