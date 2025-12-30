# HYBRID SOLUTION - FAST PDF GENERATION FOR HEROKU
import os
import subprocess
import tempfile
import time
from jinja2 import Template
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FuturesTimeoutError

# Import WeasyPrint for fast PDF generation
try:
    from weasyprint import HTML, CSS
    WEASYPRINT_AVAILABLE = True
    print("✅ WeasyPrint available - using fast PDF generation")
except (ImportError, OSError, Exception) as e:
    WEASYPRINT_AVAILABLE = False
    print(f"⚠️ WeasyPrint not available - falling back to wkhtmltopdf. Error: {e}")

# CSS overrides to simplify complex layouts for faster PDF generation
WEASYPRINT_CSS_OVERRIDES = """
/* Override flex/grid with simpler block layouts for faster PDF rendering */
.market-cards-grid {
    display: block !important;
}
.market-card {
    display: block !important;
    margin-bottom: 16px !important;
    page-break-inside: avoid !important;
}
.market-title, .content-title, .revenue-title, .section-header {
    display: block !important;
}
.market-card-header, .content-section-header, .revenue-analysis-header {
    display: block !important;
}
.two-columns {
    display: block !important;
}
.column {
    display: block !important;
    margin-bottom: 16px !important;
}
.priority-title {
    display: block !important;
}
.revenue-item {
    display: block !important;
    margin-bottom: 12px !important;
}
.content-subsection-header {
    display: block !important;
}
/* Ensure page breaks work properly */
.page-break {
    page-break-before: always !important;
    break-before: page !important;
}
"""

def _weasyprint_generate(rendered_html, output_path, css_override):
    """Internal function to run WeasyPrint PDF generation (for timeout wrapper)"""
    html_doc = HTML(string=rendered_html)
    css = CSS(string=css_override)
    html_doc.write_pdf(output_path, stylesheets=[css])
    return True

def generate_html_pdf_fast(optimization_data, output_path, timeout_seconds=20):
    """
    FAST PDF generation using WeasyPrint - optimized for Heroku with timeout
    """
    print("⚡ Starting FAST WeasyPrint PDF generation...")
    start_time = time.time()
    
    # Load and render template
    try:
        print("📋 Loading template for WeasyPrint...")
        
        template_paths = [
            os.path.join(os.path.dirname(__file__), '..', 'templates', 'professional_report_template.html'),
            os.path.join('/app', 'templates', 'professional_report_template.html')
        ]
        
        template_content = None
        for template_path in template_paths:
            if os.path.exists(template_path):
                with open(template_path, 'r', encoding='utf-8') as f:
                    template_content = f.read()
                print(f"✅ Template loaded from: {template_path}")
                break
        
        if not template_content:
            print("❌ Template not found for WeasyPrint")
            return False
        
        # Render template with data
        print("🎨 Rendering template...")
        template = Template(template_content)
        rendered_html = template.render(**optimization_data)
        print("✅ Template rendered")
        
        # Generate PDF using WeasyPrint with timeout protection
        print(f"🚀 Generating PDF with WeasyPrint (timeout: {timeout_seconds}s)...")
        
        # Use ThreadPoolExecutor for timeout handling (works on Heroku)
        with ThreadPoolExecutor(max_workers=1) as executor:
            future = executor.submit(_weasyprint_generate, rendered_html, output_path, WEASYPRINT_CSS_OVERRIDES)
            try:
                future.result(timeout=timeout_seconds)
            except FuturesTimeoutError:
                print(f"⏱️ WeasyPrint timeout after {timeout_seconds} seconds")
                return False
        
        execution_time = time.time() - start_time
        
        # Verify PDF was created
        if os.path.exists(output_path):
            pdf_size = os.path.getsize(output_path)
            if pdf_size > 5000:
                print(f"🎉 FAST WeasyPrint SUCCESS! PDF: {pdf_size:,} bytes in {execution_time:.2f} seconds")
                return True
            else:
                print(f"❌ PDF too small: {pdf_size} bytes")
        else:
            print("❌ PDF not created by WeasyPrint")
        
        return False
        
    except FuturesTimeoutError:
        print(f"⏱️ WeasyPrint timed out after {timeout_seconds} seconds")
        return False
    except Exception as e:
        print(f"❌ WeasyPrint error: {e}")
        return False

def generate_html_pdf_slow(optimization_data, output_path):
    """
    BACKUP: Optimized wkhtmltopdf with aggressive timeout for Heroku
    """
    print("🐌 Using BACKUP wkhtmltopdf method...")
    
    # Check system package location first, then fallback to compiled version
    possible_paths = ['/usr/bin/wkhtmltopdf', '/usr/local/bin/wkhtmltopdf', '/app/bin/wkhtmltopdf']
    wkhtmltopdf_cmd = None
    
    for path in possible_paths:
        if os.path.exists(path):
            wkhtmltopdf_cmd = path
            break
    
    if not wkhtmltopdf_cmd:
        wkhtmltopdf_cmd = '/app/bin/wkhtmltopdf'  # Default to Heroku location
    
    print(f"🎯 Using wkhtmltopdf: {wkhtmltopdf_cmd}")
    
    # Load and render template
    try:
        print("📋 Loading template...")
        
        template_paths = [
            os.path.join(os.path.dirname(__file__), '..', 'templates', 'professional_report_template.html'),
            os.path.join('/app', 'templates', 'professional_report_template.html')
        ]
        
        template_content = None
        for template_path in template_paths:
            if os.path.exists(template_path):
                with open(template_path, 'r', encoding='utf-8') as f:
                    template_content = f.read()
                print(f"✅ Template loaded from: {template_path}")
                break
        
        if not template_content:
            print("❌ Template not found")
            return False
        
        # Render template
        template = Template(template_content)
        html_content = template.render(**optimization_data)
        print("✅ Template rendered")
        
    except Exception as e:
        print(f"❌ Template error: {e}")
        return False
    
    # Save temporary HTML
    try:
        with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False, 
                                       encoding='utf-8', dir='/tmp') as temp_file:
            temp_file.write(html_content)
            temp_html_path = temp_file.name
        
        print(f"✅ HTML saved: {temp_html_path}")
        
    except Exception as e:
        print(f"❌ HTML save failed: {e}")
        return False
    
    # Generate PDF - AGGRESSIVE SPEED OPTIMIZATIONS
    try:
        print("🚀 SPEED-OPTIMIZED PDF generation...")
        
        cmd = [
            'xvfb-run', '-a', '--server-args=-screen 0 800x600x16',  # Smaller screen, less memory
            wkhtmltopdf_cmd,
            '--page-size', 'A4',
            '--margin-top', '0.5in',      # Smaller margins = faster
            '--margin-right', '0.5in',
            '--margin-bottom', '0.5in', 
            '--margin-left', '0.5in',
            '--encoding', 'UTF-8',
            '--enable-local-file-access',
            '--disable-smart-shrinking',   # Faster processing
            '--disable-javascript',       # No JS = much faster
            '--load-error-handling', 'ignore',  # Ignore load errors
            '--zoom', '0.75',              # Smaller zoom = faster
            '--dpi', '72',                # Lower DPI = faster
            temp_html_path,
            output_path
        ]
        
        print(f"🔧 Fast command: wkhtmltopdf [optimized] -> {output_path}")
        
        start_time = time.time()
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=20,  # AGGRESSIVE 20-second timeout for Heroku
            cwd='/tmp'
        )
        
        execution_time = time.time() - start_time
        print(f"⏱️ Completed in {execution_time:.2f} seconds")
        
        # LENIENT success detection - accept exit code 1 if PDF exists and is reasonable size
        pdf_created = os.path.exists(output_path)
        pdf_size = os.path.getsize(output_path) if pdf_created else 0
        
        if pdf_created and pdf_size > 10000:  # Accept if >10KB
            print(f"⚡ BACKUP SUCCESS! PDF: {pdf_size:,} bytes (exit code: {result.returncode})")
            return True
        else:
            print(f"❌ wkhtmltopdf failed: {result.returncode}, size: {pdf_size}")
            if result.stderr:
                print(f"Error: {result.stderr}")
        
        return False
        
    except subprocess.TimeoutExpired:
        print("❌ wkhtmltopdf timeout after 20 seconds")
        return False
    except Exception as e:
        print(f"❌ PDF generation error: {e}")
        return False
    
    finally:
        # Quick cleanup
        try:
            if 'temp_html_path' in locals() and os.path.exists(temp_html_path):
                os.unlink(temp_html_path)
                print("✅ Cleaned up temp file")
        except:
            pass

def generate_simple_text_pdf(optimization_data, output_path):
    """
    EMERGENCY FALLBACK: Generate a simple text-based PDF when all else fails
    Uses basic HTML that WeasyPrint can render quickly
    """
    print("📄 Generating simple text-based PDF as fallback...")
    
    try:
        # Extract key data
        title = optimization_data.get('title', 'Property Analysis Report')
        optimized_title = optimization_data.get('optimized_title', '')
        optimized_description = optimization_data.get('optimized_description', '')
        amenities = optimization_data.get('amenities', [])
        
        # Create simple HTML
        simple_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                body {{ font-family: Arial, sans-serif; padding: 40px; line-height: 1.6; }}
                h1 {{ color: #4285f4; border-bottom: 2px solid #4285f4; padding-bottom: 10px; }}
                h2 {{ color: #333; margin-top: 30px; }}
                .section {{ background: #f8f9fa; padding: 20px; margin: 20px 0; border-radius: 8px; }}
                ul {{ padding-left: 20px; }}
                li {{ margin-bottom: 8px; }}
            </style>
        </head>
        <body>
            <h1>🏠 STR Listing Optimization Report</h1>
            <p><strong>Property:</strong> {title}</p>
            
            <h2>✨ Optimized Title</h2>
            <div class="section">{optimized_title or 'See full report for optimized title'}</div>
            
            <h2>📝 Optimized Description</h2>
            <div class="section">{optimized_description or 'See full report for optimized description'}</div>
            
            <h2>🎯 Recommended Amenities</h2>
            <div class="section">
                <ul>
                    {''.join(f'<li>{a}</li>' for a in (amenities[:10] if amenities else ['Contact us for amenity recommendations']))}
                </ul>
            </div>
            
            <p style="margin-top: 40px; color: #666; font-size: 12px;">
                Generated by STR Optimizer - optimizemystr.com<br>
                For the full detailed report, please contact support.
            </p>
        </body>
        </html>
        """
        
        html_doc = HTML(string=simple_html)
        html_doc.write_pdf(output_path)
        
        if os.path.exists(output_path) and os.path.getsize(output_path) > 1000:
            print("✅ Simple fallback PDF generated successfully")
            return True
        return False
        
    except Exception as e:
        print(f"❌ Simple PDF fallback also failed: {e}")
        return False

def generate_html_pdf(optimization_data, output_path):
    """
    HYBRID APPROACH - Try fast WeasyPrint first, fallback to optimized wkhtmltopdf, 
    then simple text PDF as last resort
    """
    print("🚀 Starting HYBRID PDF generation...")
    
    # Try the fast WeasyPrint approach first (with shorter timeout for Heroku)
    if WEASYPRINT_AVAILABLE:
        try:
            if generate_html_pdf_fast(optimization_data, output_path, timeout_seconds=18):
                print("✅ Fast WeasyPrint succeeded!")
                return True
        except Exception as e:
            print(f"⚠️ WeasyPrint failed: {e}")
    
    # Fallback to optimized wkhtmltopdf approach
    print("🔄 Falling back to optimized wkhtmltopdf...")
    
    try:
        if generate_html_pdf_slow(optimization_data, output_path):
            print("✅ Backup wkhtmltopdf succeeded!")
            return True
    except Exception as e:
        print(f"❌ Backup wkhtmltopdf also failed: {e}")
    
    # Last resort: Generate simple text-based PDF
    if WEASYPRINT_AVAILABLE:
        print("🔄 Trying simple text PDF as last resort...")
        try:
            if generate_simple_text_pdf(optimization_data, output_path):
                print("✅ Simple text PDF succeeded!")
                return True
        except Exception as e:
            print(f"❌ Simple text PDF also failed: {e}")
    
    print("❌ All PDF generation methods failed")
    return False 