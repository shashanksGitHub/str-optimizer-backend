# NUCLEAR OPTION - SIMPLIFIED FOR GUARANTEED SUCCESS
import os
import subprocess
import tempfile
import time
from jinja2 import Template

# Add WeasyPrint import
try:
    from weasyprint import HTML, CSS
    WEASYPRINT_AVAILABLE = True
    print("✅ WeasyPrint available - using fast PDF generation")
except ImportError:
    WEASYPRINT_AVAILABLE = False
    print("⚠️ WeasyPrint not available - falling back to wkhtmltopdf")

def generate_html_pdf_fast(optimization_data, output_path):
    """ULTRA-FAST PDF generation using WeasyPrint (5-10 seconds vs 25+ for wkhtmltopdf)"""
    
    if not WEASYPRINT_AVAILABLE:
        print("❌ WeasyPrint not available, falling back to slow method")
        return generate_html_pdf_slow(optimization_data, output_path)
    
    print("🚀 FAST PDF GENERATION using WeasyPrint...")
    start_time = time.time()
    
    try:
        # Load template
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
        
        # Render template with data
        print("🎨 Rendering template...")
        template = Template(template_content)
        rendered_html = template.render(**optimization_data)
        print("✅ Template rendered")
        
        # Generate PDF directly from HTML string (SIMPLIFIED)
        print("📄 Converting HTML to PDF with WeasyPrint...")
        
        # Add CSS directly to HTML for faster processing
        enhanced_html = f"""
        <style>
        @page {{ 
            margin: 0.5in; 
            size: A4;
        }}
        body {{ 
            font-family: -apple-system, BlinkMacSystemFont, sans-serif !important;
            line-height: 1.4;
        }}
        </style>
        {rendered_html}
        """
        
        # Simple WeasyPrint call without external CSS
        html_doc = HTML(string=enhanced_html)
        html_doc.write_pdf(output_path)
        
        execution_time = time.time() - start_time
        print(f"⚡ FAST PDF completed in {execution_time:.2f} seconds")
        
        # Verify PDF was created
        if os.path.exists(output_path):
            pdf_size = os.path.getsize(output_path)
            if pdf_size > 50000:  # 50KB minimum
                print(f"🎉 FAST PDF SUCCESS! Size: {pdf_size:,} bytes")
                return True
            else:
                print(f"❌ PDF too small: {pdf_size} bytes")
        else:
            print("❌ PDF file not created")
            
        return False
        
    except Exception as e:
        print(f"❌ Fast PDF generation failed: {e}")
        print("⚠️ Falling back to slow wkhtmltopdf method...")
        return generate_html_pdf_slow(optimization_data, output_path)

def generate_html_pdf(optimization_data, output_path):
    """Main entry point - tries fast method first, falls back to slow"""
    return generate_html_pdf_fast(optimization_data, output_path)

def generate_html_pdf_slow(optimization_data, output_path):
    """SLOW PDF generation using wkhtmltopdf (backup method)"""
    print("🐌 Using SLOW wkhtmltopdf method...")
    print("🔥 NUCLEAR OPTION - STARTING PDF GENERATION...")
    
    # Heroku buildpack installs wkhtmltopdf at /app/bin/wkhtmltopdf
    heroku_path = '/app/bin/wkhtmltopdf'
    local_paths = ['/usr/bin/wkhtmltopdf', '/usr/local/bin/wkhtmltopdf']
    
    # Check Heroku path first, then local development paths
    if os.path.exists(heroku_path):
        wkhtmltopdf_cmd = heroku_path
    else:
        wkhtmltopdf_cmd = None
        for path in local_paths:
            if os.path.exists(path):
                wkhtmltopdf_cmd = path
                break
        
        if not wkhtmltopdf_cmd:
            wkhtmltopdf_cmd = heroku_path  # Default to Heroku path for production
    
    print(f"🎯 Using NUCLEAR wkhtmltopdf: {wkhtmltopdf_cmd}")
    
    # Quick verification it exists
    if not os.path.exists(wkhtmltopdf_cmd):
        print(f"🚨 IMPOSSIBLE! wkhtmltopdf not at expected location: {wkhtmltopdf_cmd}")
        print("This should NEVER happen with the nuclear Docker image!")
        return False
    
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
    
    # Generate PDF - NUCLEAR COMMAND
    try:
        print("🚀 NUCLEAR PDF GENERATION...")
        
        # SPEED-OPTIMIZED command to finish under 30 seconds
        cmd = [
            'xvfb-run', '-a', '--server-args=-screen 0 1024x768x24',  # Smaller screen = faster
            wkhtmltopdf_cmd,
            '--page-size', 'A4',
            '--margin-top', '0.5in',        # Smaller margins = faster
            '--margin-right', '0.5in', 
            '--margin-bottom', '0.5in',
            '--margin-left', '0.5in',
            '--encoding', 'UTF-8',
            '--disable-plugins',            # Speed optimizations
            '--disable-javascript',         # No JS = much faster
            '--disable-external-links',     # No external requests
            '--disable-internal-links',
            '--no-background',              # Skip background rendering
            '--load-error-handling', 'ignore',  # Ignore any load errors
            '--load-media-error-handling', 'ignore',
            '--javascript-delay', '0',      # No JS delay
            '--no-stop-slow-scripts',
            '--zoom', '0.9',                # Slightly smaller = faster
            temp_html_path,
            output_path
        ]
        
        print(f"🔧 Command: {' '.join(cmd[:3])} ... {temp_html_path} {output_path}")
        
        start_time = time.time()
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=25,  # Must finish under Heroku's 30-second limit
            cwd='/tmp'
        )
        
        execution_time = time.time() - start_time
        print(f"⏱️ Completed in {execution_time:.2f} seconds")
        
        # Check results with enhanced debugging
        print(f"🔍 Return code: {result.returncode}")
        print(f"🔍 PDF file exists: {os.path.exists(output_path)}")
        if os.path.exists(output_path):
            pdf_size = os.path.getsize(output_path)
            print(f"🔍 PDF size: {pdf_size} bytes")
        
        # Always show stdout and stderr for debugging
        if result.stdout:
            print(f"📤 STDOUT: {result.stdout}")
        if result.stderr:
            print(f"📤 STDERR: {result.stderr}")
        
        # Check if PDF was created successfully regardless of exit code
        pdf_created = os.path.exists(output_path)
        pdf_size = os.path.getsize(output_path) if pdf_created else 0
        
        # Handle successful creation
        if pdf_created and pdf_size > 100000:  # 100KB minimum for valid PDF
            if result.returncode == 0:
                print(f"🎉 PERFECT SUCCESS! PDF: {pdf_size:,} bytes")
                return True
            elif result.returncode == 1 and result.stdout and "network error" in result.stdout.lower():
                print(f"🎉 SUCCESS WITH NETWORK WARNINGS! PDF: {pdf_size:,} bytes")
                print("💡 wkhtmltopdf completed PDF generation but had network issues loading remote images")
                return True
            else:
                print(f"🎉 PDF GENERATED SUCCESSFULLY! PDF: {pdf_size:,} bytes (exit code: {result.returncode})")
                return True
        
        # Handle failures
        if result.returncode == 0:
            if not pdf_created:
                print("❌ PDF not created despite success code")
            else:
                print(f"❌ PDF too small: {pdf_size} bytes")
        else:
            print(f"❌ wkhtmltopdf failed with exit code: {result.returncode}")
            if not pdf_created:
                print("❌ No PDF file was created")
            else:
                print(f"❌ PDF created but too small: {pdf_size} bytes")
        
        return False
        
    except Exception as e:
        print(f"❌ PDF generation error: {e}")
        return False
    
    finally:
        # Cleanup
        try:
            if 'temp_html_path' in locals() and os.path.exists(temp_html_path):
                os.unlink(temp_html_path)
                print("✅ Cleaned up temp file")
        except:
            pass 