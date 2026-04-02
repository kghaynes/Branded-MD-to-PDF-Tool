#!/usr/bin/env python3
"""
Branded PDF Generator: Convert markdown files to PDFs with company branding,
headers, footers, and data classification labels.
"""

import argparse
import os
import sys
from pathlib import Path
from typing import Tuple, Dict, Any
import re

import yaml
from markdown2 import markdown
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.colors import HexColor, transparent
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, PageTemplate, Frame,
    PageBreak, Table, TableStyle, Image, KeepTogether, Preformatted
)
from reportlab.pdfgen import canvas as pdfcanvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus.flowables import HRFlowable
from reportlab.lib import colors
from PIL import Image as PILImage
import pypdf

# Register Noto Emoji font for emoji rendering
_emoji_font_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'NotoEmoji.ttf')
if os.path.exists(_emoji_font_path):
    pdfmetrics.registerFont(TTFont('NotoEmoji', _emoji_font_path))

def _html_to_rl_text(html_snippet: str) -> str:
    """Convert HTML inline markup to ReportLab Paragraph-compatible XML."""
    import html as html_mod
    text = html_snippet
    # Preserve line breaks
    text = re.sub(r'<br\s*/?>', '<br/>', text)
    # Inline code: extract, escape for XML, wrap in Courier font
    def code_to_rl(m):
        content = re.sub(r'<[^>]+>', '', m.group(1))
        content = html_mod.unescape(content)
        content = content.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
        return f'<font name="Courier" size="9">{content}</font>'
    text = re.sub(r'<code>(.*?)</code>', code_to_rl, text, flags=re.DOTALL)
    # Bold and italic
    text = re.sub(r'<strong>(.*?)</strong>', r'<b>\1</b>', text, flags=re.DOTALL)
    text = re.sub(r'<em>(.*?)</em>', r'<i>\1</i>', text, flags=re.DOTALL)
    # Links — keep anchor text, drop URL
    text = re.sub(r'<a[^>]*>(.*?)</a>', r'\1', text, flags=re.DOTALL)
    # Strip remaining HTML tags
    text = re.sub(r'<(?!b>|/b>|i>|/i>|br/>|font[^>]*>|/font>)[^>]+>', '', text)
    # Handle &nbsp;
    text = text.replace('&nbsp;', ' ')
    return _wrap_emoji(text)


def _wrap_emoji(text: str) -> str:
    """Wrap emoji characters in <font> tags to use NotoEmoji font."""
    if not os.path.exists(_emoji_font_path):
        return text
    result = []
    in_emoji = False
    for ch in text:
        if ord(ch) > 0x2000 and ord(ch) not in (0x2014,):  # Skip em dash
            if not in_emoji:
                result.append('<font name="NotoEmoji">')
                in_emoji = True
            result.append(ch)
        else:
            if in_emoji:
                result.append('</font>')
                in_emoji = False
            result.append(ch)
    if in_emoji:
        result.append('</font>')
    return ''.join(result)


class BrandedCanvas(pdfcanvas.Canvas):
    """Custom canvas that draws header/footer on every page."""

    def __init__(self, filename, generator=None, classification=None, total_pages=None, **kwargs):
        super().__init__(filename, **kwargs)
        self.generator = generator
        self.classification = classification
        self.total_pages = total_pages

    def showPage(self):
        """Draw header/footer before showing page."""
        self._draw_header_footer()
        self._draw_classification()
        super().showPage()

    def _draw_header_footer(self):
        """Draw header and footer on page."""
        self.saveState()
        self.setFont("Helvetica", 9)

        # HEADER: Logo and company info
        header_y = letter[1] - 0.5*inch

        # Logo (left side) - constrain to header area, vertically centered with text
        logo_path = self.generator.config.get('company', {}).get('logo_path')
        if logo_path and os.path.exists(logo_path):
            try:
                img = PILImage.open(logo_path)
                max_logo_height = 0.4*inch
                logo_width = (max_logo_height / img.height) * img.width
                # Center logo vertically between header_y and the header line
                logo_y = header_y - 0.35*inch + (0.35*inch - max_logo_height) / 2
                self.drawImage(logo_path, 0.5*inch, logo_y,
                              width=logo_width, height=max_logo_height)
            except Exception:
                pass

        # Company info (right side)
        company_name = self.generator.config.get('company', {}).get('name', 'Company Name')
        company_email = self.generator.config.get('company', {}).get('email', '')
        company_website = self.generator.config.get('company', {}).get('website', '')

        right_edge = letter[0] - 0.5*inch  # Align with right body margin

        self.setFont("Helvetica-Bold", 11)
        self.drawRightString(right_edge, header_y, company_name)

        self.setFont("Helvetica", 9)
        self.drawRightString(right_edge, header_y - 0.2*inch, f"Email: {company_email}")
        self.drawRightString(right_edge, header_y - 0.35*inch, f"Web: {company_website}")

        # Header line: 1pt solid line below header, across body width
        self.setStrokeColor(HexColor('#000000'))
        self.setLineWidth(1)
        header_line_y = header_y - 0.45*inch
        self.line(0.5*inch, header_line_y, letter[0] - 0.5*inch, header_line_y)

        # Footer line: 1pt solid line above footer, across body width
        footer_line_y = 0.6*inch
        self.line(0.5*inch, footer_line_y, letter[0] - 0.5*inch, footer_line_y)

        # FOOTER: Classification (left), date (center), page number (right) — all on same line
        from datetime import date
        footer_text_y = 0.35*inch

        # Page numbers (right)
        self.setFont("Helvetica", 9)
        page_num = f"Page {self._pageNumber} of {self.total_pages}" if self.total_pages else f"Page {self._pageNumber}"
        self.drawRightString(letter[0] - 0.5*inch, footer_text_y, page_num)

        # Date created (center)
        today = date.today().strftime("%B %d, %Y")
        self.drawCentredString(letter[0] / 2, footer_text_y, today)

        self.restoreState()

    def _draw_classification(self):
        """Draw classification label in footer."""
        if not self.classification:
            return

        color, text_color = self.generator._get_classification_colors(self.classification)

        self.saveState()

        # Background box — aligned with footer text line at 0.35*inch
        box_width = 2*inch
        box_height = 0.22*inch
        x = 0.5*inch
        box_y = 0.35*inch - 0.04*inch  # Align bottom of text with other footer items

        self.setFillColor(HexColor(color))
        self.rect(x, box_y, box_width, box_height, fill=1, stroke=1)

        # Text centered in box
        self.setFont("Helvetica-Bold", 11)
        self.setFillColor(HexColor(text_color))
        self.drawString(x + 0.05*inch, box_y + 0.04*inch, self.classification)

        self.restoreState()


class BrandedPDFGenerator:
    """Generate branded PDFs from markdown files with classification labels."""

    def __init__(self, config_path: str):
        """Initialize with configuration file."""
        self.config = self._load_config(config_path)
        self.styles = self._create_styles()
        self.page_number = 0

    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """Load YAML configuration file."""
        try:
            with open(config_path, 'r') as f:
                config = yaml.safe_load(f)
            return config
        except FileNotFoundError:
            raise FileNotFoundError(f"Configuration file not found: {config_path}")
        except yaml.YAMLError as e:
            raise ValueError(f"Invalid YAML configuration: {e}")

    def _create_styles(self) -> Dict[str, ParagraphStyle]:
        """Create custom paragraph styles."""
        styles = getSampleStyleSheet()

        # Heading styles
        styles.add(ParagraphStyle(
            name='CustomH1',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=HexColor(self.config.get('style', {}).get('heading_color', '#000000')),
            spaceAfter=12,
            leading=28
        ))
        styles.add(ParagraphStyle(
            name='CustomH2',
            parent=styles['Heading2'],
            fontSize=18,
            textColor=HexColor(self.config.get('style', {}).get('heading_color', '#000000')),
            spaceAfter=10,
            leading=22
        ))
        styles.add(ParagraphStyle(
            name='CustomH3',
            parent=styles['Heading3'],
            fontSize=14,
            textColor=HexColor(self.config.get('style', {}).get('heading_color', '#000000')),
            spaceAfter=8,
            leading=17
        ))
        styles.add(ParagraphStyle(
            name='CustomH4',
            parent=styles['Heading4'],
            fontSize=12,
            textColor=HexColor(self.config.get('style', {}).get('heading_color', '#000000')),
            spaceAfter=6,
            leading=15
        ))
        styles.add(ParagraphStyle(
            name='CustomH5',
            parent=styles['Heading5'],
            fontSize=11,
            textColor=HexColor(self.config.get('style', {}).get('heading_color', '#000000')),
            spaceAfter=4,
            leading=14
        ))
        styles.add(ParagraphStyle(
            name='CustomH6',
            parent=styles['Heading6'],
            fontSize=10,
            textColor=HexColor(self.config.get('style', {}).get('heading_color', '#444444')),
            spaceAfter=4,
            leading=13
        ))
        styles.add(ParagraphStyle(
            name='BulletItem',
            parent=styles['BodyText'],
            leftIndent=20,
            bulletIndent=6,
            spaceBefore=2,
            spaceAfter=2,
        ))
        styles.add(ParagraphStyle(
            name='Blockquote',
            parent=styles['BodyText'],
            leftIndent=30,
            rightIndent=10,
            textColor=HexColor('#555555'),
            borderPadding=(4, 4, 4, 8),
        ))

        return styles

    def _parse_markdown(self, md_file: str) -> Tuple[Dict[str, Any], str]:
        """
        Parse markdown file into frontmatter and content.
        Frontmatter is YAML block at start of file enclosed by ---.
        """
        with open(md_file, 'r', encoding='utf-8') as f:
            content = f.read()

        frontmatter = {}
        lines = content.split('\n')

        if lines[0].strip() == '---':
            end_marker = None
            for i, line in enumerate(lines[1:], 1):
                if line.strip() == '---':
                    end_marker = i
                    break

            if end_marker:
                frontmatter_text = '\n'.join(lines[1:end_marker])
                try:
                    frontmatter = yaml.safe_load(frontmatter_text) or {}
                except yaml.YAMLError:
                    pass
                content = '\n'.join(lines[end_marker + 1:])

        return frontmatter, content

    def _get_actual_page_count(self, pdf_path: str) -> int:
        """Get actual page count from generated PDF."""
        try:
            with open(pdf_path, 'rb') as f:
                reader = pypdf.PdfReader(f)
                return len(reader.pages)
        except Exception as e:
            print(f"Warning: Could not read page count: {e}")
            return 1

    def _markdown_to_elements(self, md_content: str) -> list:
        """Convert markdown content to Platypus elements."""
        import html as html_mod
        elements = []

        html_content = markdown(md_content, extras=['tables', 'fenced-code-blocks'])

        blocks = re.split(
            r'(<h[1-6][^>]*>.*?</h[1-6]>|<p>.*?</p>|<ul>.*?</ul>|<ol>.*?</ol>'
            r'|<pre>.*?</pre>|<table>.*?</table>|<blockquote>.*?</blockquote>|<hr[^>]*/?>)',
            html_content, flags=re.DOTALL
        )

        for block in blocks:
            block = block.strip()
            if not block:
                continue

            if block.startswith('<h1'):
                text = _html_to_rl_text(re.sub(r'</?h1[^>]*>', '', block))
                elements.append(Paragraph(text, self.styles['CustomH1']))
                elements.append(Spacer(1, 0.15*inch))
            elif block.startswith('<h2'):
                text = _html_to_rl_text(re.sub(r'</?h2[^>]*>', '', block))
                elements.append(Paragraph(text, self.styles['CustomH2']))
                elements.append(Spacer(1, 0.12*inch))
            elif block.startswith('<h3'):
                text = _html_to_rl_text(re.sub(r'</?h3[^>]*>', '', block))
                elements.append(Paragraph(text, self.styles['CustomH3']))
                elements.append(Spacer(1, 0.1*inch))
            elif block.startswith('<h4'):
                text = _html_to_rl_text(re.sub(r'</?h4[^>]*>', '', block))
                elements.append(Paragraph(text, self.styles['CustomH4']))
                elements.append(Spacer(1, 0.08*inch))
            elif block.startswith('<h5'):
                text = _html_to_rl_text(re.sub(r'</?h5[^>]*>', '', block))
                elements.append(Paragraph(text, self.styles['CustomH5']))
                elements.append(Spacer(1, 0.06*inch))
            elif block.startswith('<h6'):
                text = _html_to_rl_text(re.sub(r'</?h6[^>]*>', '', block))
                elements.append(Paragraph(text, self.styles['CustomH6']))
                elements.append(Spacer(1, 0.06*inch))
            elif block.startswith('<pre'):
                text = re.sub(r'<[^>]+>', '', block)
                text = html_mod.unescape(text).strip('\n')
                code_style = ParagraphStyle('CodeBlock', fontName='Courier', fontSize=8, leading=10)
                elements.append(Preformatted(text, code_style))
                elements.append(Spacer(1, 0.1*inch))
            elif block.startswith('<ul') or block.startswith('<ol'):
                ordered = block.startswith('<ol')
                items = re.findall(r'<li>(.*?)</li>', block, flags=re.DOTALL)
                for i, item in enumerate(items):
                    # Strip nested list blocks for simplicity
                    item = re.sub(r'<[uo]l>.*?</[uo]l>', '', item, flags=re.DOTALL)
                    item_text = _html_to_rl_text(item)
                    bullet = f'{i + 1}.' if ordered else '•'
                    elements.append(Paragraph(item_text, self.styles['BulletItem'], bulletText=bullet))
                elements.append(Spacer(1, 0.1*inch))
            elif block.startswith('<blockquote'):
                inner = re.sub(r'</?blockquote[^>]*>', '', block)
                text = _html_to_rl_text(inner)
                elements.append(Paragraph(text, self.styles['Blockquote']))
                elements.append(Spacer(1, 0.1*inch))
            elif block.startswith('<hr'):
                elements.append(HRFlowable(width='100%', thickness=1, color=HexColor('#CCCCCC'), spaceAfter=6))
                elements.append(Spacer(1, 0.05*inch))
            elif block.startswith('<p'):
                text = _html_to_rl_text(re.sub(r'</?p[^>]*>', '', block))
                elements.append(Paragraph(text, self.styles['BodyText']))
                elements.append(Spacer(1, 0.1*inch))
            elif block.startswith('<table'):
                table_data = []
                header_rows = 0
                rows = re.findall(r'<tr>(.*?)</tr>', block, flags=re.DOTALL)
                for row in rows:
                    header_cells = re.findall(r'<th[^>]*>(.*?)</th>', row, flags=re.DOTALL)
                    data_cells = re.findall(r'<td[^>]*>(.*?)</td>', row, flags=re.DOTALL)
                    if header_cells:
                        cells = [Paragraph(_html_to_rl_text(re.sub(r'<[^>]+>', '', c).strip()),
                                 ParagraphStyle('TH', fontName='Helvetica-Bold', fontSize=9))
                                 for c in header_cells]
                        table_data.append(cells)
                        header_rows += 1
                    elif data_cells:
                        cells = [Paragraph(_html_to_rl_text(re.sub(r'<[^>]+>', '', c).strip()),
                                 ParagraphStyle('TD', fontName='Helvetica', fontSize=9))
                                 for c in data_cells]
                        table_data.append(cells)

                if table_data:
                    col_count = max(len(row) for row in table_data)
                    col_width = (letter[0] - 1.5*inch) / col_count
                    tbl = Table(table_data, colWidths=[col_width] * col_count)
                    style_cmds = [
                        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                        ('ROWBACKGROUNDS', (0, 0), (-1, -1), [colors.white, HexColor('#F5F5F5')]),
                        ('TOPPADDING', (0, 0), (-1, -1), 4),
                        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
                        ('LEFTPADDING', (0, 0), (-1, -1), 6),
                        ('RIGHTPADDING', (0, 0), (-1, -1), 6),
                        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                    ]
                    if header_rows:
                        style_cmds.append(('BACKGROUND', (0, 0), (-1, header_rows - 1), HexColor('#D0D0D0')))
                    tbl.setStyle(TableStyle(style_cmds))
                    elements.append(tbl)
                    elements.append(Spacer(1, 0.15*inch))
            else:
                text = _html_to_rl_text(block)
                if text.strip():
                    elements.append(Paragraph(text, self.styles['BodyText']))
                    elements.append(Spacer(1, 0.1*inch))

        return elements

    def _get_classification_colors(self, classification: str) -> Tuple[str, str]:
        """Get color for classification level."""
        colors_config = self.config.get('classifications', {})
        default_colors = {
            'PUBLIC': '#22AA22',
            'INTERNAL': '#FFDD00',
            'CONFIDENTIAL': '#FF9900',
            'SECRET': '#DD2222'
        }

        color_config = colors_config.get(classification, {})
        color = color_config.get('color', default_colors.get(classification, '#999999'))
        text_color = color_config.get('text_color', '#FFFFFF')

        return color, text_color

    def _add_header_footer_with_total(self, canvas_obj, doc, total_pages):
        """Add header with logo and company info, footer with page numbers including total."""
        canvas_obj.saveState()

        # Set font for header/footer
        canvas_obj.setFont("Helvetica", 9)

        # HEADER: Logo and company info
        header_y = letter[1] - 0.5*inch

        # Logo (left side)
        logo_path = self.config.get('company', {}).get('logo_path')
        if logo_path and os.path.exists(logo_path):
            try:
                img = PILImage.open(logo_path)
                logo_width = 0.8*inch
                logo_height = (logo_width / img.width) * img.height
                canvas_obj.drawImage(logo_path, 0.5*inch, header_y - logo_height,
                                   width=logo_width, height=logo_height)
            except Exception as e:
                print(f"Warning: Could not load logo: {e}")

        # Company info (right side)
        company_name = self.config.get('company', {}).get('name', 'Company Name')
        company_email = self.config.get('company', {}).get('email', '')
        company_website = self.config.get('company', {}).get('website', '')

        canvas_obj.setFont("Helvetica-Bold", 11)
        canvas_obj.drawString(4.5*inch, header_y, company_name)

        canvas_obj.setFont("Helvetica", 9)
        canvas_obj.drawString(4.5*inch, header_y - 0.2*inch, f"Email: {company_email}")
        canvas_obj.drawString(4.5*inch, header_y - 0.35*inch, f"Web: {company_website}")

        # FOOTER: Page numbers with total count
        canvas_obj.setFont("Helvetica", 9)
        page_num = f"Page {doc.page} of {total_pages}"
        canvas_obj.drawString(letter[0] - 2.0*inch, 0.5*inch, page_num)

        canvas_obj.restoreState()

    def _add_header_footer(self, canvas_obj, doc, total_pages=None):
        """Add header with logo and company info, footer with page numbers."""
        canvas_obj.saveState()

        # Set font for header/footer
        canvas_obj.setFont("Helvetica", 9)

        # HEADER: Logo and company info
        header_y = letter[1] - 0.5*inch

        # Logo (left side)
        logo_path = self.config.get('company', {}).get('logo_path')
        if logo_path and os.path.exists(logo_path):
            try:
                img = PILImage.open(logo_path)
                logo_width = 0.8*inch
                logo_height = (logo_width / img.width) * img.height
                canvas_obj.drawImage(logo_path, 0.5*inch, header_y - logo_height,
                                   width=logo_width, height=logo_height)
            except Exception as e:
                print(f"Warning: Could not load logo: {e}")

        # Company info (right side)
        company_name = self.config.get('company', {}).get('name', 'Company Name')
        company_email = self.config.get('company', {}).get('email', '')
        company_website = self.config.get('company', {}).get('website', '')

        canvas_obj.setFont("Helvetica-Bold", 11)
        canvas_obj.drawString(4.5*inch, header_y, company_name)

        canvas_obj.setFont("Helvetica", 9)
        canvas_obj.drawString(4.5*inch, header_y - 0.2*inch, f"Email: {company_email}")
        canvas_obj.drawString(4.5*inch, header_y - 0.35*inch, f"Web: {company_website}")

        # FOOTER: Page numbers
        canvas_obj.setFont("Helvetica", 9)
        page_num = f"Page {doc.page}"
        canvas_obj.drawString(letter[0] - 1.5*inch, 0.5*inch, page_num)

        canvas_obj.restoreState()

    def _add_classification_label(self, canvas_obj, classification: str):
        """Add classification label to footer only."""
        color, text_color = self._get_classification_colors(classification)

        # Bottom label only
        self._draw_classification_box(canvas_obj, classification, color, text_color,
                                     x=0.5*inch, y=0.2*inch)

    def _draw_classification_box(self, canvas_obj, text: str, bg_color: str,
                                text_color: str, x: float, y: float):
        """Draw a classification label box."""
        canvas_obj.saveState()

        # Background box
        box_width = 2*inch
        box_height = 0.25*inch
        canvas_obj.setFillColor(HexColor(bg_color))
        canvas_obj.rect(x, y - box_height, box_width, box_height, fill=1, stroke=1)

        # Text
        canvas_obj.setFont("Helvetica-Bold", 11)
        canvas_obj.setFillColor(HexColor(text_color))
        canvas_obj.drawString(x + 0.05*inch, y - 0.18*inch, text)

        canvas_obj.restoreState()

    def generate(self, input_md: str, output_pdf: str, classification: str = "INTERNAL"):
        """
        Generate branded PDF from markdown file.

        Args:
            input_md: Path to markdown file
            output_pdf: Path to output PDF file
            classification: Data classification level (PUBLIC, INTERNAL, CONFIDENTIAL, SECRET)
        """
        if not os.path.exists(input_md):
            raise FileNotFoundError(f"Markdown file not found: {input_md}")

        # Validate classification
        valid_classifications = ['PUBLIC', 'INTERNAL', 'CONFIDENTIAL', 'SECRET']
        if classification not in valid_classifications:
            raise ValueError(f"Invalid classification. Must be one of: {valid_classifications}")

        # Parse markdown
        frontmatter, md_content = self._parse_markdown(input_md)

        # Build elements first
        elements = self._markdown_to_elements(md_content)

        # Create PDF document with custom canvas
        doc = SimpleDocTemplate(
            output_pdf,
            pagesize=letter,
            rightMargin=0.75*inch,
            leftMargin=0.75*inch,
            topMargin=1.2*inch,  # Space for header
            bottomMargin=0.6*inch,  # Space for footer
            title=frontmatter.get('title', 'Document'),
            author=self.config.get('company', {}).get('name', ''),
        )

        def make_canvas(filename, **kwargs):
            return BrandedCanvas(filename, generator=self, classification=classification, total_pages=None, **kwargs)

        # Build PDF - first pass (to get page count)
        try:
            doc.build(elements, canvasmaker=make_canvas)
        except Exception as e:
            raise RuntimeError(f"Failed to generate PDF: {e}")

        # Get actual page count and rebuild with correct "Page X of Y" footer
        try:
            actual_pages = self._get_actual_page_count(output_pdf)
            elements = self._markdown_to_elements(md_content)

            def make_canvas_with_total(filename, **kwargs):
                return BrandedCanvas(filename, generator=self, classification=classification, total_pages=actual_pages, **kwargs)

            doc2 = SimpleDocTemplate(
                output_pdf,
                pagesize=letter,
                rightMargin=0.75*inch,
                leftMargin=0.75*inch,
                topMargin=1.2*inch,
                bottomMargin=0.6*inch,
                title=frontmatter.get('title', 'Document'),
                author=self.config.get('company', {}).get('name', ''),
            )
            doc2.build(elements, canvasmaker=make_canvas_with_total)
        except Exception as e:
            print(f"Warning: Could not add page count: {e}")

        print(f"✓ PDF generated successfully: {output_pdf}")
        print(f"  Classification: {classification}")
        print(f"  Document title: {frontmatter.get('title', 'Untitled')}")
        print(f"  Pages: {actual_pages if 'actual_pages' in locals() else '?'}")


def main():
    """Command-line interface."""
    parser = argparse.ArgumentParser(
        description='Convert markdown to branded PDF with company branding and data classification'
    )
    parser.add_argument('input', help='Input markdown file')
    parser.add_argument('-o', '--output', help='Output PDF file (default: input.pdf)')
    parser.add_argument('-c', '--classification',
                       choices=['PUBLIC', 'INTERNAL', 'CONFIDENTIAL', 'SECRET'],
                       default='INTERNAL',
                       help='Data classification level (default: INTERNAL)')
    parser.add_argument('--config', default='config.yaml',
                       help='Configuration file (default: config.yaml)')

    args = parser.parse_args()

    # Determine output filename
    output = args.output or Path(args.input).stem + '.pdf'

    try:
        generator = BrandedPDFGenerator(args.config)
        generator.generate(args.input, output, args.classification)
    except Exception as e:
        print(f"✗ Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
