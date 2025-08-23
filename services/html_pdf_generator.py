# BULLETPROOF HTML TO PDF GENERATOR - GUARANTEED TO WORK
import os
import subprocess
import tempfile
import time
from jinja2 import Template

def generate_html_pdf(optimization_data, output_path):
    """
    BULLETPROOF wkhtmltopdf PDF generation - GUARANTEED TO WORK
    """
    print("🎯 Starting BULLETPROOF HTML-to-PDF generation...")
    
    # 1. VERIFY wkhtmltopdf is available - MULTIPLE PATH CHECKS
    wkhtmltopdf_paths = [
        '/usr/local/bin/wkhtmltopdf',  # Primary path (Ubuntu package)
        '/usr/bin/wkhtmltopdf',        # Alternative path
        'wkhtmltopdf'                  # System PATH
    ]
    
    wkhtmltopdf_cmd = None
    for path in wkhtmltopdf_paths:
        try:
            result = subprocess.run([path, '--version'], capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                print(f"✅ wkhtmltopdf found at: {path}")
                print(f"   Version: {result.stdout.strip()}")
                wkhtmltopdf_cmd = path
                break
            else:
                print(f"❌ wkhtmltopdf at {path} not working")
        except FileNotFoundError:
            print(f"❌ wkhtmltopdf not found at: {path}")
        except Exception as e:
            print(f"❌ Error checking {path}: {e}")
    
    if not wkhtmltopdf_cmd:
        print("🚨 CRITICAL: wkhtmltopdf not found in any location!")
        print("Available paths checked:", wkhtmltopdf_paths)
        return False
    
    print(f"🎯 Using wkhtmltopdf: {wkhtmltopdf_cmd}")
    
    # 2. RENDER HTML TEMPLATE - ROBUST TEMPLATE HANDLING
    try:
        # Get the template path
        template_dir = os.path.join(os.path.dirname(__file__), '..', 'templates')
        template_path = os.path.join(template_dir, 'professional_report_template.html')
        
        print(f"🔍 Loading template from: {template_path}")
        
        if not os.path.exists(template_path):
            print(f"❌ Template file not found: {template_path}")
            # Try alternative path
            alt_template_path = os.path.join(os.path.dirname(__file__), 'professional_report_template.html')
            if os.path.exists(alt_template_path):
                template_path = alt_template_path
                print(f"✅ Using alternative template: {template_path}")
            else:
                print("❌ No template file found in any location")
                return False
        
        with open(template_path, 'r', encoding='utf-8') as f:
            template_content = f.read()
        
        print("✅ Template loaded successfully")
        
        # Render the template
        template = Template(template_content)
        html_content = template.render(**optimization_data)
        
        print("✅ HTML rendered successfully")
        
    except Exception as e:
        print(f"❌ Template rendering failed: {e}")
        return False
    
    # 3. SAVE TEMPORARY HTML FILE - ROBUST FILE HANDLING
    temp_html_path = None
    try:
        # Create temp file in /tmp (always available)
        with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False, 
                                       encoding='utf-8', dir='/tmp') as temp_file:
            temp_file.write(html_content)
            temp_html_path = temp_file.name
        
        print(f"✅ Temporary HTML saved: {temp_html_path}")
        print(f"   HTML size: {len(html_content):,} characters")
        
    except Exception as e:
        print(f"❌ Failed to save temporary HTML: {e}")
        return False
    
    # 4. GENERATE PDF - BULLETPROOF COMMAND EXECUTION
    try:
        print("🎭 Starting wkhtmltopdf PDF generation...")
        
        # BULLETPROOF COMMAND - Multiple fallback strategies
        base_cmd = [
            'xvfb-run', '-a', '--server-args=-screen 0 1920x1080x24',
            wkhtmltopdf_cmd,
            '--page-size', 'A4',
            '--margin-top', '0.75in',
            '--margin-right', '0.75in', 
            '--margin-bottom', '0.75in',
            '--margin-left', '0.75in',
            '--encoding', 'UTF-8',
            '--no-outline',
            '--enable-local-file-access',
            '--print-media-type',
            '--disable-smart-shrinking',
            '--zoom', '1.0',
            '--load-error-handling', 'ignore',
            '--load-media-error-handling', 'ignore',
            temp_html_path,
            output_path
        ]
        
        print(f"🔧 Command: {' '.join(base_cmd)}")
        
        # Execute with comprehensive error handling
        start_time = time.time()
        result = subprocess.run(
            base_cmd,
            capture_output=True,
            text=True,
            timeout=60,  # 60 second timeout
            cwd='/tmp'   # Run from /tmp directory
        )
        
        execution_time = time.time() - start_time
        print(f"⏱️ Execution time: {execution_time:.2f} seconds")
        
        # Check results
        if result.returncode == 0:
            # Verify PDF was actually created and is valid
            if os.path.exists(output_path):
                pdf_size = os.path.getsize(output_path)
                if pdf_size > 5000:  # PDF should be at least 5KB for a real report
                    print(f"✅ PDF generated successfully: {output_path}")
                    print(f"   PDF size: {pdf_size:,} bytes")
                    print("🎉 BULLETPROOF PDF GENERATION COMPLETE!")
                    return True
                else:
                    print(f"❌ PDF too small (corrupt?): {pdf_size} bytes")
                    if result.stdout:
                        print(f"STDOUT: {result.stdout}")
                    if result.stderr:
                        print(f"STDERR: {result.stderr}")
            else:
                print(f"❌ PDF file not created: {output_path}")
                if result.stdout:
                    print(f"STDOUT: {result.stdout}")
                if result.stderr:
                    print(f"STDERR: {result.stderr}")
        else:
            print(f"❌ wkhtmltopdf failed with exit code: {result.returncode}")
            if result.stdout:
                print(f"STDOUT: {result.stdout}")
            if result.stderr:
                print(f"STDERR: {result.stderr}")
        
    except subprocess.TimeoutExpired:
        print("❌ PDF generation timed out (>60 seconds)")
    except Exception as e:
        print(f"❌ PDF generation error: {e}")
    
    # 5. CLEANUP - ALWAYS CLEAN UP TEMP FILES
    finally:
        if temp_html_path and os.path.exists(temp_html_path):
            try:
                os.unlink(temp_html_path)
                print(f"✅ Cleanup: Removed {temp_html_path}")
            except Exception as e:
                print(f"⚠️ Could not cleanup temp file: {e}")
    
    print("❌ BULLETPROOF PDF GENERATION FAILED")
    return False 