# Quick Start Guide

Get your branded PDF generator running in 5 minutes.

## Step 1: Install Dependencies

```bash
pip install -r requirements.txt
```

## Step 2: Prepare Your Company Logo

- Place your company logo (PNG or JPG) in this directory
- Note the filename (e.g., `logo.png`)

## Step 3: Configure Company Information

Edit `config.yaml`:

```yaml
company:
  name: "Acme Corp"
  email: "security@acme.com"
  website: "www.acme.com"
  logo_path: "logo.png"  # Update this path
```

Save and close the file.

## Step 4: Test with Example Document

```bash
python md_to_pdf.py example_doc.md -o test.pdf --classification CONFIDENTIAL
```

Open `test.pdf` to verify everything looks good:
- Your company name in header (top right)
- Company logo (top left)
- "CONFIDENTIAL" label (orange) at top and bottom
- Example content formatted properly

## Step 5: Use with Your Own Documents

For any markdown file, generate a branded PDF:

```bash
python md_to_pdf.py your_document.md -o output.pdf --classification INTERNAL
```

Choose classification based on sensitivity:
- `PUBLIC` - No restrictions
- `INTERNAL` - Internal use only
- `CONFIDENTIAL` - Restricted distribution
- `SECRET` - Highly restricted

## Optional: Add to Your Tools

If your markdown generators create `.md` files, add a post-processing step:

```bash
# After generating document.md:
python /path/to/md_to_pdf.py document.md -o document.pdf --classification INTERNAL
```

## Customization

### Change Classification Colors

Edit the `classifications` section in `config.yaml` with hex color codes:

```yaml
classifications:
  CONFIDENTIAL:
    color: "#FF6600"        # Your color
    text_color: "#FFFFFF"
```

### Add More Metadata

Frontmatter in your markdown files becomes PDF metadata:

```markdown
---
title: "Report Title"
author: "John Doe"
date: "2026-03-31"
---

# Content starts here...
```

### Adjust Margins and Spacing

Modify the `page` section in `config.yaml` to change spacing and margins.

## Common Commands

```bash
# Default (INTERNAL classification)
python md_to_pdf.py file.md -o file.pdf

# Public document
python md_to_pdf.py file.md -o file.pdf --classification PUBLIC

# Confidential document
python md_to_pdf.py file.md -o file.pdf --classification CONFIDENTIAL

# With custom config
python md_to_pdf.py file.md -o file.pdf --config custom.yaml --classification SECRET
```

## Need Help?

See `README.md` for full documentation and troubleshooting.
