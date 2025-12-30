# PDF Generation using pdfkit (wkhtmltopdf) - Fast and reliable
import os
import tempfile
import time
import pdfkit
from jinja2 import Template

# Set Qt to use offscreen platform (required for headless wkhtmltopdf)
os.environ['QT_QPA_PLATFORM'] = 'offscreen'

# Configure pdfkit to find wkhtmltopdf
# Heroku with Apt buildpack installs to /app/.apt/usr/bin/wkhtmltopdf
WKHTMLTOPDF_PATHS = [
    '/app/.apt/usr/bin/wkhtmltopdf',  # Heroku with Apt buildpack
    '/usr/local/bin/wkhtmltopdf',      # macOS with Homebrew
    '/usr/bin/wkhtmltopdf',            # Linux system install
]

def get_pdfkit_config():
    """Get pdfkit configuration with correct wkhtmltopdf path"""
    for path in WKHTMLTOPDF_PATHS:
        if os.path.exists(path):
            print(f"✅ Found wkhtmltopdf at: {path}")
            return pdfkit.configuration(wkhtmltopdf=path)
    
    # If not found in common paths, let pdfkit find it in PATH
    print("⚠️ wkhtmltopdf not found in common paths, using system PATH")
    return None

def get_pdfkit_options():
    """Get optimized pdfkit options for fast, high-quality PDF generation"""
    # Note: Some options like --print-media-type and --image-quality 
    # are not supported with unpatched Qt (Ubuntu's wkhtmltopdf)
    return {
        'page-size': 'A4',
        'margin-top': '15mm',
        'margin-right': '15mm',
        'margin-bottom': '25mm',
        'margin-left': '15mm',
        'encoding': 'UTF-8',
        'enable-local-file-access': None,  # Allow local file access for images
        'no-stop-slow-scripts': None,      # Don't stop slow scripts
        'disable-javascript': None,        # Disable JS for faster rendering
        'no-background': False,            # Keep backgrounds
        'lowquality': False,               # Keep quality high
        'dpi': 150,                         # Good balance of quality and speed
        'quiet': None,                      # Suppress wkhtmltopdf output
    }

def load_template():
    """Load the HTML template from available paths"""
    template_paths = [
        os.path.join(os.path.dirname(__file__), '..', 'templates', 'professional_report_template.html'),
        os.path.join('/app', 'templates', 'professional_report_template.html'),
        os.path.join(os.path.dirname(__file__), 'templates', 'professional_report_template.html'),
    ]
    
    for template_path in template_paths:
        if os.path.exists(template_path):
            with open(template_path, 'r', encoding='utf-8') as f:
                content = f.read()
            print(f"✅ Template loaded from: {template_path}")
            return content
    
    raise FileNotFoundError(f"Template not found in paths: {template_paths}")

def generate_html_pdf(optimization_data, output_path):
    """
    Generate PDF using pdfkit (wkhtmltopdf) - Fast WebKit-based rendering
    
    This is the primary and only PDF generation method.
    wkhtmltopdf uses WebKit rendering engine which handles modern CSS
    including flexbox much better than WeasyPrint.
    """
    print("🚀 Starting pdfkit PDF generation...")
    start_time = time.time()
    
    try:
        # Step 1: Load template
        print("📋 Loading template...")
        template_content = load_template()
        
        # Step 2: Render template with data
        print("🎨 Rendering template with data...")
        template = Template(template_content)
        rendered_html = template.render(**optimization_data)
        print(f"✅ Template rendered ({len(rendered_html):,} characters)")
        
        # Step 3: Get pdfkit configuration
        config = get_pdfkit_config()
        options = get_pdfkit_options()
        
        # Step 4: Generate PDF
        print("📄 Generating PDF with wkhtmltopdf...")
        
        # Save HTML to temp file first (more reliable than string input for complex HTML)
        with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False, 
                                         encoding='utf-8', dir='/tmp') as temp_file:
            temp_file.write(rendered_html)
            temp_html_path = temp_file.name
        
        try:
            if config:
                pdfkit.from_file(temp_html_path, output_path, options=options, configuration=config)
            else:
                pdfkit.from_file(temp_html_path, output_path, options=options)
        finally:
            # Clean up temp file
            if os.path.exists(temp_html_path):
                os.unlink(temp_html_path)
        
        # Step 5: Verify PDF was created successfully
        execution_time = time.time() - start_time
        
        if os.path.exists(output_path):
            pdf_size = os.path.getsize(output_path)
            if pdf_size > 5000:  # Minimum reasonable PDF size
                print(f"🎉 PDF generated successfully!")
                print(f"   📊 Size: {pdf_size:,} bytes")
                print(f"   ⏱️ Time: {execution_time:.2f} seconds")
                return True
            else:
                print(f"❌ PDF too small ({pdf_size} bytes), generation may have failed")
                return False
        else:
            print("❌ PDF file was not created")
            return False
            
    except Exception as e:
        execution_time = time.time() - start_time
        print(f"❌ PDF generation failed after {execution_time:.2f}s: {str(e)}")
        
        # Log more details for debugging
        import traceback
        print(f"📋 Full error traceback:")
        traceback.print_exc()
        
        return False


# Legacy function name for backwards compatibility
def generate_html_pdf_fast(optimization_data, output_path):
    """Legacy wrapper - calls generate_html_pdf"""
    return generate_html_pdf(optimization_data, output_path)
