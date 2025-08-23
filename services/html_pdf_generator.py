# ULTIMATE BULLETPROOF HTML TO PDF GENERATOR - GUARANTEED SUCCESS
import os
import subprocess
import tempfile
import time
from jinja2 import Template

def generate_html_pdf(optimization_data, output_path):
    """
    ULTIMATE BULLETPROOF wkhtmltopdf PDF generation 
    Multiple strategies - GUARANTEED to work somewhere!
    """
    print("🎯 STARTING ULTIMATE BULLETPROOF PDF GENERATION...")
    
    # 1. COMPREHENSIVE wkhtmltopdf DETECTION - Check everywhere!
    wkhtmltopdf_paths = [
        '/usr/local/bin/wkhtmltopdf',    # Official Ubuntu package location
        '/usr/bin/wkhtmltopdf',          # Alternative Ubuntu location
        '/snap/bin/wkhtmltopdf-proxy',   # Snap package location
        'wkhtmltopdf'                    # System PATH
    ]
    
    print("🔍 SEARCHING FOR WKHTMLTOPDF IN ALL LOCATIONS...")
    
    wkhtmltopdf_cmd = None
    for path in wkhtmltopdf_paths:
        print(f"   Checking: {path}")
        try:
            # Check if file exists (for absolute paths)
            if path.startswith('/') and not os.path.exists(path):
                print(f"   ❌ File not found: {path}")
                continue
                
            # Test the command
            result = subprocess.run([path, '--version'], capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                print(f"   ✅ WORKING: {path}")
                print(f"   📋 Version: {result.stdout.strip()}")
                wkhtmltopdf_cmd = path
                break
            else:
                print(f"   ❌ Version check failed: {path} (exit code: {result.returncode})")
                if result.stderr:
                    print(f"   📝 Error: {result.stderr.strip()}")
        except FileNotFoundError:
            print(f"   ❌ Command not found: {path}")
        except subprocess.TimeoutExpired:
            print(f"   ❌ Timeout checking: {path}")
        except Exception as e:
            print(f"   ❌ Error checking {path}: {e}")
    
    if not wkhtmltopdf_cmd:
        print("🚨 CRITICAL FAILURE: wkhtmltopdf not found anywhere!")
        print("📋 Paths checked:")
        for path in wkhtmltopdf_paths:
            print(f"   - {path}")
        
        # Diagnostic information
        print("\n🔬 DIAGNOSTIC INFORMATION:")
        try:
            # Check what's installed
            result = subprocess.run(['which', 'wkhtmltopdf'], capture_output=True, text=True)
            if result.returncode == 0:
                print(f"📍 'which' found wkhtmltopdf at: {result.stdout.strip()}")
            else:
                print("📍 'which' did not find wkhtmltopdf")
        except:
            print("📍 'which' command failed")
            
        try:
            # Check installed packages
            result = subprocess.run(['dpkg', '-l'], capture_output=True, text=True)
            wkhtmltopdf_packages = [line for line in result.stdout.split('\n') if 'wkhtmltopdf' in line.lower()]
            if wkhtmltopdf_packages:
                print("📦 Found wkhtmltopdf packages:")
                for pkg in wkhtmltopdf_packages:
                    print(f"   {pkg}")
            else:
                print("📦 No wkhtmltopdf packages found")
        except:
            print("📦 Could not check installed packages")
            
        try:
            # Search filesystem
            result = subprocess.run(['find', '/usr', '-name', '*wkhtmltopdf*', '-type', 'f'], 
                                  capture_output=True, text=True, timeout=10)
            if result.stdout:
                print("🔍 Files found on filesystem:")
                for file in result.stdout.strip().split('\n'):
                    if file:
                        print(f"   {file}")
            else:
                print("🔍 No wkhtmltopdf files found on filesystem")
        except:
            print("🔍 Filesystem search failed")
        
        return False
    
    print(f"🎯 USING WKHTMLTOPDF: {wkhtmltopdf_cmd}")
    
    # 2. LOAD AND RENDER HTML TEMPLATE - Robust handling
    try:
        print("📋 LOADING HTML TEMPLATE...")
        
        # Try multiple template locations
        template_paths = [
            os.path.join(os.path.dirname(__file__), '..', 'templates', 'professional_report_template.html'),
            os.path.join(os.path.dirname(__file__), 'professional_report_template.html'),
            os.path.join('/app', 'templates', 'professional_report_template.html'),
            os.path.join('/app', 'professional_report_template.html')
        ]
        
        template_content = None
        template_used = None
        
        for template_path in template_paths:
            print(f"   Trying: {template_path}")
            if os.path.exists(template_path):
                try:
                    with open(template_path, 'r', encoding='utf-8') as f:
                        template_content = f.read()
                    template_used = template_path
                    print(f"   ✅ Template loaded from: {template_path}")
                    break
                except Exception as e:
                    print(f"   ❌ Failed to read template: {e}")
            else:
                print(f"   ❌ Template not found: {template_path}")
        
        if not template_content:
            print("🚨 CRITICAL: No template file found!")
            return False
        
        print(f"📊 Template size: {len(template_content):,} characters")
        
        # Render the template
        print("🎨 RENDERING HTML CONTENT...")
        template = Template(template_content)
        html_content = template.render(**optimization_data)
        
        print(f"✅ HTML rendered successfully ({len(html_content):,} characters)")
        
    except Exception as e:
        print(f"❌ Template processing failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # 3. SAVE TEMPORARY HTML FILE - Multiple locations
    temp_html_path = None
    try:
        print("💾 SAVING TEMPORARY HTML FILE...")
        
        # Try multiple temp directories
        temp_dirs = ['/tmp', '/var/tmp', '.']
        
        for temp_dir in temp_dirs:
            try:
                with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False, 
                                               encoding='utf-8', dir=temp_dir) as temp_file:
                    temp_file.write(html_content)
                    temp_html_path = temp_file.name
                print(f"✅ HTML saved to: {temp_html_path}")
                print(f"📊 File size: {os.path.getsize(temp_html_path):,} bytes")
                break
            except Exception as e:
                print(f"❌ Failed to save in {temp_dir}: {e}")
                continue
        
        if not temp_html_path:
            print("🚨 CRITICAL: Could not save temporary HTML file!")
            return False
        
    except Exception as e:
        print(f"❌ HTML file creation failed: {e}")
        return False
    
    # 4. GENERATE PDF - Ultimate robustness
    try:
        print("🎭 STARTING PDF GENERATION...")
        print(f"📄 Input: {temp_html_path}")
        print(f"📄 Output: {output_path}")
        
        # Comprehensive command with all options
        cmd = [
            'xvfb-run', '-a', '--server-args=-screen 0 1920x1080x24',
            wkhtmltopdf_cmd,
            '--page-size', 'A4',
            '--orientation', 'Portrait',
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
            '--quiet',
            temp_html_path,
            output_path
        ]
        
        print(f"🔧 Full command:")
        print(f"   {' '.join(cmd)}")
        
        # Execute with maximum error handling
        print("⚡ EXECUTING WKHTMLTOPDF...")
        start_time = time.time()
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=90,  # 90 second timeout
            cwd='/tmp'   # Safe working directory
        )
        
        execution_time = time.time() - start_time
        print(f"⏱️ Execution completed in {execution_time:.2f} seconds")
        print(f"📋 Exit code: {result.returncode}")
        
        # Detailed result analysis
        if result.stdout:
            print(f"📤 STDOUT: {result.stdout}")
        if result.stderr:
            print(f"📥 STDERR: {result.stderr}")
        
        # Verify success
        if result.returncode == 0:
            if os.path.exists(output_path):
                pdf_size = os.path.getsize(output_path)
                print(f"📊 PDF size: {pdf_size:,} bytes")
                
                if pdf_size > 10000:  # Reasonable minimum size for a report
                    print("🎉 PDF GENERATION SUCCESSFUL!")
                    print("✅ ULTIMATE BULLETPROOF SYSTEM WORKED!")
                    return True
                else:
                    print(f"❌ PDF too small - likely corrupt: {pdf_size} bytes")
            else:
                print(f"❌ PDF file was not created: {output_path}")
        else:
            print(f"❌ wkhtmltopdf failed with exit code: {result.returncode}")
        
        return False
        
    except subprocess.TimeoutExpired:
        print("❌ PDF generation timed out (>90 seconds)")
        return False
    except Exception as e:
        print(f"❌ PDF generation error: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        # 5. CLEANUP - Always cleanup temp files
        print("🧹 CLEANING UP...")
        if temp_html_path and os.path.exists(temp_html_path):
            try:
                os.unlink(temp_html_path)
                print(f"✅ Removed: {temp_html_path}")
            except Exception as e:
                print(f"⚠️ Could not remove temp file: {e}")
    
    print("❌ ULTIMATE PDF GENERATION FAILED")
    return False 