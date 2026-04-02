# Quick Start Guide

Get your branded PDF generator running in 5 minutes.

## Step 1: Set Up the Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate   # macOS/Linux
venv\Scripts\activate      # Windows
python3 -m ensurepip --upgrade
pip install -r requirements.txt
```

> **macOS note:** If pip gives an "externally managed environment" error, make sure you activated the venv first. If the venv is already active and the error persists, recreate it:
> ```bash
> deactivate && rm -rf venv && python3 -m venv venv && source venv/bin/activate && python3 -m ensurepip --upgrade && pip install -r requirements.txt
> ```

## Step 2: Verify the Emoji Font is Present

The file `NotoEmoji.ttf` must be in the same directory as `md_to_pdf.py`. It is bundled in the repo. If it's missing, re-download it:

```bash
curl -L -o NotoEmoji.ttf "https://github.com/google/fonts/raw/main/ofl/notoemoji/NotoEmoji%5Bwght%5D.ttf"
```

## Step 3: Configure Company Information

Edit `config.yaml`:

```yaml
company:
  name: "Acme Corp"
  email: "security@acme.com"
  website: "www.acme.com"
  logo_path: "/absolute/path/to/logo.png"  # PNG or JPG
```

## Step 4: Test with Example Document

```bash
python3 md_to_pdf.py example_doc.md -o test.pdf --classification CONFIDENTIAL
```

Open `test.pdf` and verify:
- Company name/email/website in header (top right)
- Company logo (top left)
- "CONFIDENTIAL" badge (orange) in footer
- Date and "Page X of Y" in footer
- Markdown content formatted correctly

## Step 5: Use with Your Own Documents

```bash
python3 md_to_pdf.py your_document.md -o output.pdf --classification INTERNAL
```

### Classification levels

| Flag | Badge Color | Use for |
|---|---|---|
| `PUBLIC` | Green | No restrictions |
| `INTERNAL` | Yellow | Internal use only |
| `CONFIDENTIAL` | Orange | Restricted distribution |
| `SECRET` | Red | Highly restricted |

## Common Commands

```bash
# Default (INTERNAL classification)
python3 md_to_pdf.py file.md -o file.pdf

# Public document
python3 md_to_pdf.py file.md -o file.pdf --classification PUBLIC

# Confidential with custom config
python3 md_to_pdf.py file.md -o file.pdf --config custom.yaml --classification CONFIDENTIAL
```

## Supported Markdown

Your `.md` files can use:
- Headings `#` through `######`
- **Bold**, *italic*, `inline code`
- Bullet and numbered lists
- Tables
- Fenced code blocks (``` ``` ```) — whitespace and ASCII art preserved
- Blockquotes (`>`)
- Horizontal rules (`---`)
- Emoji (✅ ❌ ⭐ etc.)
- YAML frontmatter (used as PDF metadata, not rendered in body)

## Need Help?

See `README.md` for full documentation and troubleshooting.
