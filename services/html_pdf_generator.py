# HYBRID SOLUTION - FAST PDF GENERATION FOR HEROKU
import os
import subprocess
import tempfile
import time
from jinja2 import Template

# Import WeasyPrint for fast PDF generation
try:
    from weasyprint import HTML, CSS
    WEASYPRINT_AVAILABLE = True
    print("✅ WeasyPrint available - using fast PDF generation")
except (ImportError, OSError, Exception) as e:
    WEASYPRINT_AVAILABLE = False
    print(f"⚠️ WeasyPrint not available - falling back to wkhtmltopdf. Error: {e}")

def generate_html_pdf_fast(optimization_data, output_path):
    """
    FAST PDF generation using WeasyPrint - optimized for Heroku
    """
    print("⚡ Starting FAST WeasyPrint PDF generation...")
    start_time = time.time()
    
    # Load and render template
    try:
        print("📋 Loading template for WeasyPrint...")
        
        # Determine base path for images
        base_path = None
        template_paths = [
            os.path.join(os.path.dirname(__file__), '..', 'templates', 'professional_report_template.html'),
            os.path.join('/app', 'templates', 'professional_report_template.html')
        ]
        
        template_content = None
        for template_path in template_paths:
            if os.path.exists(template_path):
                with open(template_path, 'r', encoding='utf-8') as f:
                    template_content = f.read()
                base_path = os.path.dirname(os.path.dirname(template_path))
                print(f"✅ Template loaded from: {template_path}")
                print(f"✅ Base path for images: {base_path}")
                break
        
        if not template_content:
            print("❌ Template not found for WeasyPrint")
            return False
        
        # Remove image references to speed up PDF generation (images cause slow loading)
        # Replace logo images with text placeholder to avoid slow network/file lookups
        import re
        rendered_html_clean = template_content
        # Remove img tags with logo to speed up generation
        rendered_html_clean = re.sub(
            r'<img[^>]*StrLogo[^>]*/?>', 
            '<span style="font-weight:bold;color:#4285f4;">STR</span>', 
            rendered_html_clean
        )
        
        # Render template with data
        print("🎨 Rendering template...")
        template = Template(rendered_html_clean)
        rendered_html = template.render(**optimization_data)
        print("✅ Template rendered")
        
        # Generate PDF using WeasyPrint with timeout protection
        print("🚀 Generating PDF with WeasyPrint (with timeout protection)...")
        
        import signal
        
        def timeout_handler(signum, frame):
            raise TimeoutError("WeasyPrint PDF generation timed out after 25 seconds")
        
        # Set 25 second timeout (Heroku has 30s limit)
        old_handler = None
        try:
            old_handler = signal.signal(signal.SIGALRM, timeout_handler)
            signal.alarm(25)  # 25 second timeout
            
            # Create HTML document and generate PDF
            # Use base_url to help resolve local paths, but we've removed images anyway
            html_doc = HTML(string=rendered_html, base_url=base_path)
            html_doc.write_pdf(output_path)
            
            signal.alarm(0)  # Cancel the alarm
        except TimeoutError as e:
            print(f"⏰ {e}")
            return False
        finally:
            signal.alarm(0)  # Ensure alarm is cancelled
            if old_handler:
                signal.signal(signal.SIGALRM, old_handler)
        
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
        
    except Exception as e:
        print(f"❌ WeasyPrint error: {e}")
        import traceback
        traceback.print_exc()
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

def generate_html_pdf(optimization_data, output_path):
    """
    HYBRID APPROACH - Try fast WeasyPrint first, fallback to optimized wkhtmltopdf
    """
    print("🚀 Starting HYBRID PDF generation...")
    
    # Try the fast WeasyPrint approach first
    if WEASYPRINT_AVAILABLE:
        try:
            if generate_html_pdf_fast(optimization_data, output_path):
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
    
    print("❌ All PDF generation methods failed")
    return False 