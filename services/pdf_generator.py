import os
import tempfile
import requests
from PIL import Image
import io
import re
from fpdf import FPDF

# Import the new HTML-to-PDF generator
from .html_pdf_generator import generate_html_pdf

def clean_text_for_pdf(text):
    """Helper function to clean text for PDF compatibility"""
    if not text:
        return ""
    # Replace problematic Unicode characters with ASCII equivalents
    replacements = {
        '\u2022': '* ',  # bullet point
        '\u2013': '-',   # en dash
        '\u2014': '--',  # em dash
        '\u201c': '"',   # left double quote
        '\u201d': '"',   # right double quote
        '\u2018': "'",   # left single quote
        '\u2019': "'",   # right single quote
        '\u2713': '[X] ',  # checkmark
        '✓': '[X] ',     # checkmark
        '•': '* ',       # bullet point
        '🎯': '',        # target emoji
        '📊': '',        # chart emoji
        '✍️': '',        # writing emoji
        '💰': '',        # money emoji
        '🚀': '',        # rocket emoji
        '🏞️': '',        # landscape emoji
        '🛁': '',        # bathtub emoji
        '🎱': '',        # pool ball emoji
        '🐕': '',        # dog emoji
        '🌟': '',        # star emoji
        '🍳': '',        # cooking emoji
        '🔥': '',        # fire emoji
    }
    
    result = text
    for unicode_char, replacement in replacements.items():
        result = result.replace(unicode_char, replacement)

    # Remove any remaining non-ASCII characters
    result = ''.join(char if ord(char) < 128 else '?' for char in result)
    
    return result

class ModernPDF(FPDF):
    def __init__(self):
        super().__init__()
        self.set_auto_page_break(auto=True, margin=20)
        
        # Modern color scheme matching the HTML
        self.colors = {
            'primary_blue': (37, 99, 235),        # #2563eb
            'light_blue': (219, 234, 254),        # #dbeafe
            'dark_gray': (17, 24, 39),            # #111827
            'medium_gray': (31, 41, 55),          # #1f2937
            'text_gray': (75, 85, 99),            # #4b5563
            'light_gray': (107, 114, 128),        # #6b7280
            'bg_gray': (243, 244, 246),           # #f3f4f6
            'border_gray': (229, 231, 235),       # #e5e7eb
            'success_green': (16, 185, 129),      # #10b981
            'success_bg': (209, 250, 229),        # #d1fae5
            'warning_orange': (245, 158, 11),     # #f59e0b
            'warning_bg': (254, 243, 199),        # #fef3c7
            'danger_red': (239, 68, 68),          # #ef4444
            'danger_bg': (254, 226, 226),         # #fee2e2
            'white': (255, 255, 255),
        }
    
    def header(self):
        """Modern header with blue line"""
        # Header text
        self.set_font('Arial', 'B', 18)
        self.set_text_color(*self.colors['primary_blue'])
        self.set_y(20)
        self.cell(0, 10, 'AI Property Insights', 0, 0, 'L')
        
        # Date on right
        self.set_font('Arial', '', 11)
        self.set_text_color(*self.colors['light_gray'])
        self.set_xy(140, 20)
        self.cell(0, 10, 'Analysis Date: November 2024', 0, 1, 'R')
        
        # Blue horizontal line
        self.set_draw_color(*self.colors['primary_blue'])
        self.set_line_width(2)
        self.line(20, 35, 190, 35)
        
        self.ln(20)

    def footer(self):
        """Modern footer"""
        self.set_y(-15)
        self.set_font('Arial', 'I', 9)
        self.set_text_color(*self.colors['light_gray'])
        self.cell(0, 10, f'Page {self.page_no()} of 5 | AI Property Optimization Report', 0, 0, 'C')

    def add_main_title(self, title, subtitle):
        """Add main title section matching HTML"""
        # Main title
        self.set_font('Arial', 'B', 24)
        self.set_text_color(*self.colors['dark_gray'])
        self.cell(0, 15, clean_text_for_pdf(title), 0, 1, 'L')
        
        # Subtitle in blue
        self.set_font('Arial', '', 14)
        self.set_text_color(*self.colors['primary_blue'])
        self.cell(0, 8, clean_text_for_pdf(subtitle), 0, 1, 'L')
        self.ln(10)

    def add_alert_box(self, text, alert_type='success'):
        """Add alert box matching HTML design"""
        colors = {
            'success': (self.colors['success_bg'], self.colors['success_green']),
            'info': (self.colors['light_blue'], self.colors['primary_blue']),
            'warning': (self.colors['warning_bg'], self.colors['warning_orange']),
            'danger': (self.colors['danger_bg'], self.colors['danger_red'])
        }
        
        bg_color, border_color = colors.get(alert_type, colors['info'])
        
        # Calculate box height
        self.set_font('Arial', '', 11)
        words = clean_text_for_pdf(text).split()
        lines = []
        current_line = ""
        
        for word in words:
            if self.get_string_width(current_line + " " + word) < 160:
                current_line += (" " if current_line else "") + word
            else:
                if current_line:
                    lines.append(current_line)
                current_line = word
        
        if current_line:
            lines.append(current_line)
        
        box_height = len(lines) * 6 + 16
        
        # Background
        self.set_fill_color(*bg_color)
        self.rect(20, self.get_y(), 170, box_height, 'F')
        
        # Left border
        self.set_fill_color(*border_color)
        self.rect(20, self.get_y(), 3, box_height, 'F')
        
        # Text
        self.set_text_color(*self.colors['dark_gray'])
        y_start = self.get_y() + 8
        
        for i, line in enumerate(lines):
            self.set_xy(28, y_start + i * 6)
            self.cell(0, 6, line, 0, 1, 'L')
        
        self.set_y(self.get_y() + box_height + 10)

    def add_score_grid(self, metrics):
        """Add score cards in grid layout matching reference design exactly"""
        box_width = 65   # Adjusted to match reference
        box_height = 55  # Adjusted to match reference
        spacing = 12     # Adjusted spacing to match reference
        start_x = 20
        current_y = self.get_y()

        for i, (value, label, highlight) in enumerate(metrics):
            x = start_x + i * (box_width + spacing)
            
            # Background and border colors to match reference exactly
            if highlight:
                # First card (4.98) - Blue background with blue border
                bg_color = self.colors['light_blue']
                border_color = self.colors['primary_blue']
                border_width = 2
            else:
                # Other cards - Light gray background with gray border
                bg_color = self.colors['bg_gray']
                border_color = self.colors['border_gray']
                border_width = 1
            
            # Background
            self.set_fill_color(*bg_color)
            self.rect(x, current_y, box_width, box_height, 'F')
            
            # Border
            self.set_draw_color(*border_color)
            self.set_line_width(border_width)
            self.rect(x, current_y, box_width, box_height)
            
            # Value - Large and prominent, centered
            self.set_font('Arial', 'B', 24)  # Larger font to match reference
            self.set_text_color(*self.colors['primary_blue'])
            self.set_xy(x, current_y + 16)
            self.cell(box_width, 12, clean_text_for_pdf(value), 0, 0, 'C')
            
            # Label - Smaller, below value, centered
            self.set_font('Arial', '', 10)
            self.set_text_color(*self.colors['light_gray'])
            self.set_xy(x, current_y + 35)
            self.cell(box_width, 6, clean_text_for_pdf(label), 0, 0, 'C')
        
        self.set_y(current_y + box_height + 20)  # Proper spacing after cards

    def add_section_header(self, title, icon=''):
        """Add section header with optional icon"""
        self.set_font('Arial', 'B', 16)
        self.set_text_color(*self.colors['medium_gray'])
        
        if icon:
            title = f"{icon} {title}"
        
        self.cell(0, 10, clean_text_for_pdf(title), 0, 1, 'L')
        self.ln(5)

    def add_recommendation_box(self, title, content, priority=''):
        """Add recommendation box matching reference design exactly"""
        # Calculate dynamic height based on content
        lines = content.split('\n')
        content_lines = [line for line in lines if line.strip()]  # Remove empty lines
        box_height = max(70, 25 + len(content_lines) * 5)  # Increased base height
        
        current_y = self.get_y()
        
        # Background - Light gray to match reference
        self.set_fill_color(*self.colors['bg_gray'])
        self.rect(20, current_y, 170, box_height, 'F')
        
        # Border - Light gray, thin border
        self.set_draw_color(*self.colors['border_gray'])
        self.set_line_width(0.5)
        self.rect(20, current_y, 170, box_height)
        
        # Title - Bold, dark gray, proper positioning
        self.set_xy(25, current_y + 10)
        self.set_font('Arial', 'B', 12)
        self.set_text_color(*self.colors['medium_gray'])
        self.cell(120, 8, clean_text_for_pdf(title), 0, 0, 'L')
        
        # Priority badge - Match reference exactly
        if priority:
            if priority == 'HIGH PRIORITY':
                bg_color = (254, 226, 226)  # Light red background
                text_color = (220, 38, 38)  # Red text
                badge_text = 'HIGH PRIORITY'
            elif priority == 'MEDIUM PRIORITY':
                bg_color = (254, 243, 199)  # Light yellow/orange background
                text_color = (217, 119, 6)  # Orange text
                badge_text = 'MEDIUM PRIORITY'
            else:
                bg_color = (254, 226, 226)
                text_color = (220, 38, 38)
                badge_text = priority
            
            badge_width = 42
            badge_height = 12
            
            # Badge background with rounded corners effect
            self.set_fill_color(*bg_color)
            self.rect(143, current_y + 8, badge_width, badge_height, 'F')
            
            # Badge text
            self.set_font('Arial', 'B', 7)
            self.set_text_color(*text_color)
            self.set_xy(143, current_y + 9)
            self.cell(badge_width, 10, badge_text, 0, 0, 'C')
        
        # Content - Process each line properly with better formatting
        self.set_font('Arial', '', 10)
        self.set_text_color(*self.colors['text_gray'])
        
        y_offset = current_y + 25
        for line in content_lines:
            if line.strip():
                self.set_xy(25, y_offset)
                # Handle bullet points and formatting - Clean BEFORE processing
                formatted_line = clean_text_for_pdf(line)
                
                # Ensure bullet points are properly formatted
                if line.strip().startswith('•'):
                    # Replace bullet with asterisk for PDF compatibility
                    formatted_line = '* ' + formatted_line[2:].strip() if len(formatted_line) > 2 else '* '
                
                self.cell(140, 5, formatted_line, 0, 1, 'L')
                y_offset += 5.5  # Slightly more line spacing
        
        self.set_y(current_y + box_height + 15)  # Space after box to match reference

    def add_feature_grid(self, features):
        """Add feature grid (2 columns)"""
        box_width = 80
        box_height = 60
        spacing = 10
        start_x = 20
        
        for i in range(0, len(features), 2):
            current_y = self.get_y()

            # Left box
            if i < len(features):
                self.add_feature_box(features[i], start_x, current_y, box_width, box_height)
            
            # Right box
            if i + 1 < len(features):
                self.add_feature_box(features[i + 1], start_x + box_width + spacing, current_y, box_width, box_height)
            
            self.set_y(current_y + box_height + 15)

    def add_feature_box(self, feature, x, y, width, height):
        """Add individual feature box"""
        title, description, percentage = feature
        
        # Background
        self.set_fill_color(*self.colors['bg_gray'])
        self.rect(x, y, width, height, 'F')

        # Border
        self.set_draw_color(*self.colors['border_gray'])
        self.set_line_width(0.5)
        self.rect(x, y, width, height)

        # Title
        self.set_xy(x + 5, y + 5)
        self.set_font('Arial', 'B', 11)
        self.set_text_color(*self.colors['medium_gray'])
        self.cell(0, 8, clean_text_for_pdf(title), 0, 1, 'L')
        
        # Description
        self.set_xy(x + 5, y + 15)
        self.set_font('Arial', '', 9)
        self.set_text_color(*self.colors['text_gray'])
        
        # Wrap text
        words = clean_text_for_pdf(description).split()
        lines = []
        current_line = ""
        
        for word in words:
            if self.get_string_width(current_line + " " + word) < width - 10:
                current_line += (" " if current_line else "") + word
            else:
                if current_line:
                    lines.append(current_line)
                current_line = word
        
        if current_line:
            lines.append(current_line)
        
        for i, line in enumerate(lines[:3]):  # Limit to 3 lines
            self.set_xy(x + 5, y + 15 + i * 5)
            self.cell(0, 5, line, 0, 1, 'L')
        
        # Progress bar
        bar_y = y + height - 15
        bar_width = width - 10
        
        # Background bar
        self.set_fill_color(229, 231, 235)
        self.rect(x + 5, bar_y, bar_width, 4, 'F')
        
        # Progress bar
        progress_width = (percentage / 100) * bar_width
        self.set_fill_color(*self.colors['primary_blue'])
        self.rect(x + 5, bar_y, progress_width, 4, 'F')
        
        # Percentage text
        self.set_xy(x + 5, bar_y + 6)
        self.set_font('Arial', '', 8)
        self.set_text_color(*self.colors['text_gray'])
        self.cell(0, 4, f'Market Uniqueness: {percentage}%', 0, 0, 'L')

    def add_table(self, headers, rows):
        """Add professional table"""
        col_widths = [35, 25, 20, 30, 50]  # Adjust based on content
        row_height = 8
        
        # Header
        self.set_fill_color(*self.colors['bg_gray'])
        self.set_text_color(*self.colors['medium_gray'])
        self.set_font('Arial', 'B', 10)
        
        for i, header in enumerate(headers):
            self.cell(col_widths[i], row_height, clean_text_for_pdf(header), 1, 0, 'L', True)
        self.ln()
        
        # Rows
        self.set_fill_color(*self.colors['white'])
        self.set_text_color(*self.colors['text_gray'])
        self.set_font('Arial', '', 9)
        
        for row in rows:
            for i, cell in enumerate(row):
                self.cell(col_widths[i], row_height, clean_text_for_pdf(str(cell)), 1, 0, 'L', True)
            self.ln()
        
        self.ln(10)

    def add_numbered_list(self, items):
        """Add numbered list"""
        self.set_font('Arial', '', 10)
        self.set_text_color(*self.colors['text_gray'])
        
        for i, item in enumerate(items, 1):
            self.cell(0, 6, f"{i}. {clean_text_for_pdf(item)}", 0, 1, 'L')
        
        self.ln(5)

    def add_bullet_list(self, items):
        """Add bullet list"""
        self.set_font('Arial', '', 10)
        self.set_text_color(*self.colors['text_gray'])
        
        for item in items:
            self.cell(0, 6, f"* {clean_text_for_pdf(item)}", 0, 1, 'L')
        
        self.ln(5)

    def add_final_cta(self):
        """Add final call-to-action box"""
        box_height = 35
        
        # Background
        self.set_fill_color(*self.colors['medium_gray'])
        self.rect(20, self.get_y(), 170, box_height, 'F')
        
        # Title
        self.set_font('Arial', 'B', 14)
        self.set_text_color(*self.colors['white'])
        self.set_xy(20, self.get_y() + 8)
        self.cell(170, 8, 'Ready to Transform Your Listing?', 0, 1, 'C')
        
        # Subtitle
        self.set_font('Arial', '', 10)
        self.set_xy(20, self.get_y() + 2)
        self.cell(170, 6, 'This AI-powered analysis identified 25+ optimization opportunities specific to your property.', 0, 1, 'C')
        self.set_xy(20, self.get_y())
        self.cell(170, 6, 'Implementation support and monthly performance tracking available.', 0, 1, 'C')
        
        self.ln(box_height + 10)

def generate_professional_pdf(optimization_data, output_path):
    """Generate professional PDF using HTML-to-PDF for pixel-perfect results"""
    
    # Use the HTML-to-PDF system for 100% replica - NO FALLBACK
    return generate_html_pdf(optimization_data, output_path) 