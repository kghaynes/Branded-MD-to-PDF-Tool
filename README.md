# Branded PDF Generator

A Python tool to convert markdown files to professionally branded PDFs with company branding, headers, footers, and data classification labels.

## Features

- ✓ Company logo, name, email, and website in header
- ✓ Page numbers in footer
- ✓ Data classification labels (PUBLIC, INTERNAL, CONFIDENTIAL, SECRET) with color coding
- ✓ Classification badges appear at top and bottom of each page
- ✓ Supports markdown formatting (headings, lists, tables, code blocks)
- ✓ Frontmatter metadata extracted and used as PDF properties
- ✓ YAML configuration for easy customization
- ✓ Command-line interface

## Installation

1. Install Python 3.8 or higher

2. Create and activate a virtual environment:
```bash
# Create virtual environment
python3 -m venv venv

# Activate it (macOS/Linux)
source venv/bin/activate

# Activate it (Windows)
venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

> **Note:** Each time you open a new terminal, activate the venv again with `source venv/bin/activate` (macOS/Linux) or `venv\Scripts\activate` (Windows) before running the script.

> **macOS Note:** On macOS, use `python3` and `pip3` instead of `python` and `pip` (e.g., `python3 -m venv venv`, `pip3 install -r requirements.txt`, `python3 md_to_pdf.py ...`).

## Configuration

Edit `config.yaml` with your company information:

```yaml
company:
  name: "Your Company Name"
  email: "contact@example.com"
  website: "www.example.com"
  logo_path: "/path/to/your/logo.png"
```

- **logo_path**: Should be a PNG or JPG image. Dimensions are flexible; the script scales it to fit.
- **classifications**: Customize colors for each classification level (hex color codes)

## Usage

### Basic Usage

Convert a markdown file to PDF with default INTERNAL classification:

```bash
python md_to_pdf.py document.md -o output.pdf
```

### With Custom Classification

Specify the data classification level:

```bash
python md_to_pdf.py document.md -o output.pdf --classification CONFIDENTIAL
```

### Custom Config File

Use a different configuration file:

```bash
python md_to_pdf.py document.md -o output.pdf --config my-config.yaml --classification SECRET
```

### Available Classifications

- `PUBLIC` - Green label
- `INTERNAL` - Yellow label
- `CONFIDENTIAL` - Orange label
- `SECRET` - Red label

## Markdown File Format

Your markdown files can include optional YAML frontmatter at the top:

```markdown
---
title: "Document Title"
author: "Author Name"
date: "2026-03-31"
---

# Your Document Heading

Document content in markdown format...
```

The frontmatter is extracted and used as PDF metadata (invisible to reader) but not displayed in the document content.

## Markdown Supported Elements

- Headings (H1-H3)
- Paragraphs
- Unordered and ordered lists
- Tables
- Code blocks
- Inline formatting (bold, italic, code)

## Output

The generated PDF includes:

- **Header**: Company logo (left side) and company name, email, website (right side)
- **Classification Labels**: Color-coded boxes with classification level at top-left and bottom-right
- **Content**: Formatted markdown content in the middle of each page
- **Footer**: Page numbers
- **Metadata**: Document title and author from frontmatter

## Example

Test with the included example:

```bash
python md_to_pdf.py example_doc.md -o test.pdf --classification CONFIDENTIAL
```

This generates a PDF with:
- Your company branding in the header
- "CONFIDENTIAL" label (orange) at top and bottom
- All the example document content formatted

## Troubleshooting

### Logo not appearing
- Check that the path in `config.yaml` is correct and the file exists
- Ensure the image is in PNG or JPG format
- Verify file permissions allow reading

### PDF generation fails
- Check that the markdown file is valid UTF-8 encoded
- Ensure all required fields in config.yaml are filled
- Verify the output directory exists and is writable

### Classification colors not showing
- Ensure hex color codes in config.yaml are valid (e.g., `#FF0000`)
- Check that the classification name matches exactly (case-sensitive)

## Advanced Usage

### Batch Processing

Create a script to process multiple files:

```bash
#!/bin/bash
for file in *.md; do
  python md_to_pdf.py "$file" -o "${file%.md}.pdf" --classification INTERNAL
done
```

### Custom Styling

Modify the `style` section in `config.yaml` to customize colors and fonts for the generated PDFs.

## Technical Details

- **PDF Library**: ReportLab (provides low-level control over PDF generation)
- **Markdown Parser**: markdown2 (supports tables and code blocks)
- **Configuration**: YAML format
- **Logo Handling**: Pillow for image processing

## License

Use freely within your organization.
