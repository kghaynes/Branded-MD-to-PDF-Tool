# Branded PDF Generator
v 1.01 (v1.0 was incomplete)

A Python tool to convert markdown files to professionally branded PDFs with company branding, headers, footers, and data classification labels.

## Features

- ✓ Company logo, name, email, and website in header
- ✓ Page numbers ("Page X of Y") in footer
- ✓ Data classification labels (PUBLIC, INTERNAL, CONFIDENTIAL, SECRET) with color coding
- ✓ Full markdown support — headings, lists, tables, code blocks, inline formatting, blockquotes, horizontal rules, emoji
- ✓ ASCII art and preformatted diagrams rendered with preserved spacing
- ✓ Emoji rendering via bundled Noto Emoji font
- ✓ Frontmatter metadata extracted and used as PDF properties
- ✓ YAML configuration for easy customization
- ✓ Command-line interface

## Installation

1. Install Python 3.8 or higher

2. Create and activate a virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate   # macOS/Linux
venv\Scripts\activate      # Windows
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

> **Note:** Each time you open a new terminal, activate the venv again with `source venv/bin/activate` before running the script.

> **macOS Note:** If pip gives an "externally managed environment" error, use `python3 -m pip install -r requirements.txt` inside the activated venv.

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
python3 md_to_pdf.py document.md -o output.pdf
```

### With Custom Classification

```bash
python3 md_to_pdf.py document.md -o output.pdf --classification CONFIDENTIAL
```

### Custom Config File

```bash
python3 md_to_pdf.py document.md -o output.pdf --config my-config.yaml --classification SECRET
```

### Available Classifications

| Level | Badge Color |
|---|---|
| `PUBLIC` | Green |
| `INTERNAL` | Yellow |
| `CONFIDENTIAL` | Orange |
| `SECRET` | Red |

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

The frontmatter is used as PDF metadata (not displayed in the document body).

## Supported Markdown Elements

| Element | Support |
|---|---|
| Headings H1–H6 | Full styling with configurable heading color |
| Paragraphs | With bold, italic, inline code, links |
| Unordered lists | Bullet points (•) |
| Ordered lists | Numbered |
| Tables | With header row, alternating row shading |
| Fenced code blocks | Monospace, whitespace-preserved (ASCII art safe) |
| Inline code | Courier font |
| Blockquotes | Indented with grey text |
| Horizontal rules | Grey divider line |
| Emoji | Rendered via Noto Emoji font (✅ ❌ ⭐ etc.) |
| YAML frontmatter | Extracted as PDF metadata, not rendered |

## Output

The generated PDF includes:

- **Header**: Company logo (left) and company name, email, website (right), with separator line
- **Body**: Fully formatted markdown content
- **Footer**: Classification badge (left), date created (center), "Page X of Y" (right)

## Emoji Support

Emoji are rendered using the bundled `NotoEmoji.ttf` font (Google Noto Emoji, monochrome). The font file must be present in the same directory as `md_to_pdf.py`. Emoji appear as black outline glyphs (not color).

## Example

```bash
source venv/bin/activate
python3 md_to_pdf.py example_doc.md -o report.pdf --classification CONFIDENTIAL
```

## Troubleshooting

### `ModuleNotFoundError: No module named 'yaml'`
The venv is activated but packages aren't installed, or the venv's Python was broken by a Homebrew update. Recreate it:
```bash
deactivate && rm -rf venv && python3 -m venv venv && source venv/bin/activate && python3 -m ensurepip --upgrade && pip install -r requirements.txt
```

### Logo not appearing
- Check that the path in `config.yaml` is correct and the file exists
- Ensure the image is in PNG or JPG format

### Emoji not rendering
- Ensure `NotoEmoji.ttf` is present in the same directory as `md_to_pdf.py`
- Re-download if missing: `curl -L -o NotoEmoji.ttf "https://github.com/google/fonts/raw/main/ofl/notoemoji/NotoEmoji%5Bwght%5D.ttf"`

### PDF generation fails
- Ensure the markdown file is valid UTF-8
- Verify the output directory exists and is writable

## Technical Details

| Component | Library |
|---|---|
| PDF generation | ReportLab |
| Markdown parsing | markdown2 |
| Configuration | PyYAML |
| Logo handling | Pillow |
| Page counting | pypdf |
| Emoji rendering | Noto Emoji (bundled TTF) |

## License

Use freely within your organization.
