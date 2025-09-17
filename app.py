from openai import OpenAI
import stripe
from flask import Flask, request, jsonify, send_file, render_template, redirect
from flask_cors import CORS
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
import os
import tempfile
import time
import requests
from bs4 import BeautifulSoup
import base64
from fpdf import FPDF
from PIL import Image
import io
import re
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Import custom modules
from services.airbnb_scraper import scrape_airbnb_images
from services.pdf_generator import ModernPDF
from services.email_service import send_email
from services.str_optimizer import optimize_listing

app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'your-secret-key-here')

# Health check endpoint removed - duplicate exists below

# Enable CORS for React frontend
allowed_origins = [
    "http://localhost:3000", 
    "http://localhost:3001",
    "https://str-optimizer.web.app",  # Firebase hosting
    "https://optimizemystr.com",  # Production frontend domain
    "https://str-optimizer-backend-7d9de05e5c57.herokuapp.com",  # Heroku backend URL
]

# Add ngrok URLs if specified in environment
ngrok_url = os.getenv('NGROK_URL')
if ngrok_url:
    allowed_origins.append(ngrok_url)
    allowed_origins.append(ngrok_url.replace('http://', 'https://'))  # Support both http and https

# For development, allow all origins if specified
if os.getenv('FLASK_ENV') == 'development' and os.getenv('ALLOW_ALL_ORIGINS') == 'true':
    CORS(app, origins="*")
else:
    CORS(app, origins=allowed_origins)

# Configure API keys
openai_api_key = os.getenv("OPENAI_API_KEY")
if not openai_api_key:
    print("Warning: OPENAI_API_KEY not set. AI features will be limited.")
    openai_api_key = "placeholder-key-for-development"
    
client = OpenAI(api_key=openai_api_key)

# Configure Stripe with debug logging
stripe_secret_key = os.getenv("STRIPE_SECRET_KEY")
print(f"🔑 Stripe Secret Key loaded: {'Yes' if stripe_secret_key else 'No'}")
if stripe_secret_key:
    print(f"🔑 Stripe Key starts with: {stripe_secret_key[:10]}...")
else:
    print("❌ No Stripe secret key found in environment")
    
stripe.api_key = stripe_secret_key

@app.route('/')
def index():
    return jsonify({
        'message': 'STR Optimizer Backend API',
        'version': '1.0.0',
        'status': 'running'
    })

@app.route('/health')
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'services': {
            'openai': bool(os.getenv("OPENAI_API_KEY")),
            'stripe': bool(os.getenv("STRIPE_SECRET_KEY")),
            'email': bool(os.getenv("EMAIL_USERNAME") and os.getenv("EMAIL_PASSWORD"))
        }
    })

# Scrape Airbnb listing title and description
@app.route('/api/scrape', methods=['POST'])
def scrape():
    data = request.json
    url = data.get('url')
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
        response = requests.get(url, headers=headers, timeout=15)
        soup = BeautifulSoup(response.text, 'html.parser')

        title = soup.find('meta', property='og:title')
        description = soup.find('meta', property='og:description')

        return jsonify({
            'title': title['content'] if title else '',
            'description': description['content'] if description else '',
            'success': True
        })
    except Exception as e:
        return jsonify({'error': str(e), 'success': False}), 500

@app.route('/api/optimize', methods=['POST'])
def optimize():
    """Main optimization endpoint"""
    try:
        data = request.json
        result = optimize_listing(data)
        return jsonify({
            'success': True,
            'data': result
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/create-checkout-session', methods=['POST'])
def create_checkout_session():
    try:
        data = request.json
        delivery_type = data.get('delivery_type')
        form_data = data.get('form_data', {})

        print(f"=== STRIPE CHECKOUT DEBUG ===")
        print(f"Creating checkout session for delivery_type: {delivery_type}")
        print(f"Form data: {form_data}")
        
        # Ensure Stripe API key is set
        stripe_secret_key = os.getenv("STRIPE_SECRET_KEY")
        if not stripe_secret_key:
            print("❌ ERROR: Stripe API key not found in environment")
            return jsonify({'error': 'Payment processing is not configured. Please contact support.'}), 500
        
        stripe.api_key = stripe_secret_key
        print(f"🔑 Stripe API Key: {'Set' if stripe.api_key else 'Not Set'}")
        if stripe.api_key:
            print(f"🔑 Stripe Key starts with: {stripe.api_key[:10]}...")

        # Check if Stripe is configured
        if not stripe.api_key:
            print("ERROR: Stripe API key not configured")
            return jsonify({'error': 'Payment processing is not configured. Please contact support.'}), 500

        # Set pricing based on delivery type
        if delivery_type == 'basic':
            product_name = 'STR Optimizer Basic Package'
            product_description = 'AI-optimized title, description, and amenities'
            unit_amount = 499  # $4.99
        else:  # premium
            product_name = 'STR Optimizer Premium Package'
            product_description = 'Professional PDF report with email delivery'
            unit_amount = 1999  # $19.99

        print(f"Product: {product_name}, Price: ${unit_amount/100}")

        # Get the server URL from environment variables - Updated fallback for Heroku
        server_url = os.getenv('SERVER_URL', 'https://str-optimizer-backend-7d9de05e5c57.herokuapp.com')
        success_url = server_url + '/api/payment-success?session_id={CHECKOUT_SESSION_ID}'
        cancel_url = server_url + '/api/payment-cancel'

        try:
            print("🔄 Creating Stripe checkout session...")
            checkout_session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=[{
                    'price_data': {
                        'currency': 'usd',
                        'product_data': {
                            'name': product_name,
                            'description': product_description,
                            'metadata': {
                                'delivery_type': delivery_type
                            }
                        },
                        'unit_amount': unit_amount,
                    },
                    'quantity': 1,
                }],
                mode='payment',
                success_url=success_url,
                cancel_url=cancel_url,
                metadata={
                    'delivery_type': delivery_type,
                    'url': form_data.get('url', ''),
                    'listingUrl': form_data.get('listingUrl', ''),  # Store both keys
                    'email': form_data.get('email', ''),
                    'title': form_data.get('title', ''),
                    'description': form_data.get('description', '')
                }
            )
            print(f"✅ Stripe session created successfully: {checkout_session.id}")
            return jsonify({'checkout_url': checkout_session.url})
        except Exception as stripe_error:
            print(f"❌ Stripe session creation failed: {stripe_error}")
            print(f"❌ Error type: {type(stripe_error)}")
            raise stripe_error

    except stripe.error.StripeError as e:
        print(f"❌ STRIPE ERROR: {e}")
        return jsonify({'error': f'Payment processing error: {str(e)}'}), 500
    except Exception as e:
        print(f"❌ UNEXPECTED ERROR: {e}")
        return jsonify({'error': f'Unexpected error: {str(e)}'}), 500

@app.route('/api/payment-success')
def payment_success():
    session_id = request.args.get('session_id')
    if not session_id:
        # Redirect to frontend with error
        frontend_url = os.getenv('FRONTEND_URL', 'https://str-optimizer.web.app')
        return redirect(f'{frontend_url}/payment-error?error=missing_session_id')

    try:
        # Retrieve the session from Stripe
        stripe.api_key = os.getenv("STRIPE_SECRET_KEY")
        checkout_session = stripe.checkout.Session.retrieve(session_id)
        metadata = checkout_session.metadata

        if not metadata or not metadata.get('delivery_type'):
            frontend_url = os.getenv('FRONTEND_URL', 'https://str-optimizer.web.app')
            return redirect(f'{frontend_url}/payment-error?error=invalid_session_data')
        
        delivery_type = metadata.get('delivery_type')
        form_data = {
            'url': metadata.get('url') or metadata.get('listingUrl'),  # Handle both keys
            'email': metadata.get('email'),
            'title': metadata.get('title'),
            'description': metadata.get('description')
        }

        print(f"🔍 Payment success - processing form data:")
        print(f"  URL: {form_data['url']}")
        print(f"  Email: {form_data['email']}")
        print(f"  Title: {form_data['title']}")
        print(f"  Description: {form_data['description'][:100] if form_data['description'] else 'None'}...")

        if delivery_type == 'premium':
            form_data['wants_pdf'] = True
            form_data['wants_email'] = True
        else:
            form_data['wants_pdf'] = False
            form_data['wants_email'] = False

        # Don't process optimization here - let frontend handle it with loading screen
        # Just redirect immediately to show the beautiful loading experience
        
        # Redirect to frontend success page with session_id
        frontend_url = os.getenv('FRONTEND_URL', 'https://str-optimizer.web.app')
        return redirect(f'{frontend_url}/payment-success?session_id={session_id}')
        
    except stripe.error.StripeError as e:
        print(f"❌ Stripe error in payment success: {e}")
        frontend_url = os.getenv('FRONTEND_URL', 'https://str-optimizer.web.app')
        return redirect(f'{frontend_url}/payment-error?error=stripe_error')
    except Exception as e:
        print(f"❌ Unexpected error in payment success: {e}")
        frontend_url = os.getenv('FRONTEND_URL', 'https://str-optimizer.web.app')
        return redirect(f'{frontend_url}/payment-error?error=unexpected_error')

# New endpoint for frontend to fetch optimization results
@app.route('/api/get-optimization-result/<session_id>')
def get_optimization_result(session_id):
    try:
        print(f"🔍 Fetching optimization result for session: {session_id}")
        
        # Validate session ID format
        if not session_id or not session_id.startswith('cs_'):
            return jsonify({'error': 'Invalid session ID format'}), 400
            
        # Retrieve the session from Stripe and process optimization
        stripe.api_key = os.getenv("STRIPE_SECRET_KEY")
        
        try:
            checkout_session = stripe.checkout.Session.retrieve(session_id)
        except stripe.error.InvalidRequestError as e:
            print(f"❌ Stripe session error: {e}")
            return jsonify({'error': 'Payment session has expired or is invalid. Please try making a new payment.'}), 400
            
        metadata = checkout_session.metadata
        print(f"🔍 Session metadata: {metadata}")

        if not metadata or not metadata.get('delivery_type'):
            return jsonify({'error': 'Payment session is missing required data. Please contact support.'}), 400
        
        delivery_type = metadata.get('delivery_type')
        form_data = {
            'url': metadata.get('url') or metadata.get('listingUrl'),
            'email': metadata.get('email'),
            'title': metadata.get('title'),
            'description': metadata.get('description')
        }

        print(f"🔍 Processing optimization for {delivery_type} package")
        print(f"🔍 Form data: {form_data}")

        if delivery_type == 'premium':
            form_data['wants_pdf'] = True
            form_data['wants_email'] = True
        else:
            form_data['wants_pdf'] = False
            form_data['wants_email'] = False

        result = optimize_listing(form_data)
        result['package_type'] = delivery_type

        print(f"✅ Optimization completed successfully")
        return jsonify({
            'success': True,
            'data': result
        })
    except stripe.error.StripeError as e:
        print(f"❌ Stripe API error: {e}")
        return jsonify({'error': 'Payment system error. Please contact support.'}), 500
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return jsonify({'error': 'An unexpected error occurred. Please try again or contact support.'}), 500

@app.route('/api/payment-cancel')
def payment_cancel():
    return jsonify({'message': 'Payment cancelled'})

# Legacy routes for backwards compatibility (redirect to API routes)
@app.route('/payment-success')
def payment_success_redirect():
    session_id = request.args.get('session_id')
    if session_id:
        return redirect(f'/api/payment-success?session_id={session_id}')
    return redirect('/api/payment-success')

@app.route('/payment-cancel')
def payment_cancel_redirect():
    return redirect('/api/payment-cancel')

@app.route('/api/download/<filename>', methods=['GET'])
def download(filename):
    """Download PDF files with proper error handling"""
    try:
        print(f"📥 Download request for: {filename}")
        
        # Security check - only allow PDF files
        if not filename.endswith('.pdf'):
            print(f"❌ Invalid file type requested: {filename}")
            return jsonify({'error': 'Only PDF files are allowed'}), 400
        
        # Check multiple possible locations for the file
        possible_paths = [
            os.path.join(tempfile.gettempdir(), filename),  # Standard temp directory
            os.path.join('/tmp', filename),  # Linux temp directory
            filename if os.path.isabs(filename) else None  # Absolute path
        ]
        
        file_path = None
        for path in possible_paths:
            if path and os.path.exists(path):
                file_path = path
                print(f"✅ Found file at: {file_path}")
                break
        
        if not file_path:
            print(f"❌ File not found in any location: {filename}")
            print(f"   Checked paths: {[p for p in possible_paths if p]}")
            # List files in temp directory for debugging
            temp_files = os.listdir(tempfile.gettempdir())
            pdf_files = [f for f in temp_files if f.endswith('.pdf')]
            print(f"   Available PDF files in temp: {pdf_files[:5]}")  # Show first 5
            return jsonify({
                'error': 'File not found',
                'message': 'The PDF file may have expired or been cleaned up. Please regenerate your report.',
                'available_files': pdf_files[:3]  # Show some available files for debugging
            }), 404
        
        # Check file size and permissions
        file_size = os.path.getsize(file_path)
        print(f"📊 File size: {file_size} bytes")
        
        if file_size == 0:
            print(f"❌ File is empty: {file_path}")
            return jsonify({'error': 'File is empty or corrupted'}), 500
        
        # Send file with proper headers
        return send_file(
            file_path, 
            as_attachment=True,
            download_name=f"str_optimization_report_{filename}",
            mimetype='application/pdf'
        )
        
    except FileNotFoundError as e:
        print(f"❌ FileNotFoundError: {e}")
        return jsonify({
            'error': 'File not found',
            'message': 'The PDF file may have been cleaned up. Please regenerate your report.'
        }), 404
    except Exception as e:
        print(f"❌ Download error: {e}")
        return jsonify({'error': f'Download failed: {str(e)}'}), 500

@app.route('/api/test-stripe')
def test_stripe():
    """Test Stripe configuration"""
    try:
        print("🧪 Testing Stripe configuration...")
        
        # Ensure Stripe API key is set
        stripe_secret_key = os.getenv("STRIPE_SECRET_KEY")
        if not stripe_secret_key:
            print("❌ ERROR: Stripe API key not found in environment")
            return jsonify({'error': 'Stripe API key not configured'}), 500
        
        stripe.api_key = stripe_secret_key
        print(f"🔑 Stripe API Key: {'Set' if stripe.api_key else 'Not Set'}")
        if stripe.api_key:
            print(f"🔑 Key starts with: {stripe.api_key[:10]}...")
        
        # Test a simple Stripe API call
        account = stripe.Account.retrieve()
        print(f"✅ Stripe account test successful: {account.id}")
        
        return jsonify({
            'success': True,
            'message': 'Stripe is working correctly',
            'account_id': account.id
        })
    except Exception as e:
        print(f"❌ Stripe test failed: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/test-email', methods=['POST'])
def test_email():
    """Test email functionality"""
    try:
        data = request.get_json()
        test_email_addr = data.get('email', 'test@example.com')
        
        print(f"🧪 Testing email to: {test_email_addr}")
        
        from services.email_service import send_email
        result = send_email(
            test_email_addr,
            "This is a test description for your Airbnb listing optimization.",
            "• High-speed WiFi\n• Parking space\n• Kitchen essentials",
            "Great location and clean property",
            None  # No PDF for test
        )
        
        if result:
            return jsonify({"status": "success", "message": "Test email sent successfully"})
        else:
            return jsonify({"status": "error", "message": "Email sending failed"}), 500
            
    except Exception as e:
        print(f"❌ Email test error: {e}")
        return jsonify({"status": "error", "message": f"Email test failed: {str(e)}"}), 500

# Test endpoint for PDF generation debugging
@app.route('/api/test-pdf-generation')
def test_pdf_generation():
    try:
        print("🧪 Testing PDF generation...")
        
        # Check Playwright installation
        import subprocess
        try:
            playwright_check = subprocess.run(['python', '-m', 'playwright', '--version'], 
                                            capture_output=True, text=True, timeout=10)
            print(f"🧪 Playwright version: {playwright_check.stdout.strip()}")
        except Exception as e:
            print(f"❌ Playwright check failed: {e}")
        
        # Check if chromium is available
        try:
            chromium_check = subprocess.run(['python', '-m', 'playwright', 'install', '--dry-run'], 
                                          capture_output=True, text=True, timeout=10)
            print(f"🧪 Playwright install check: {chromium_check.stdout.strip()}")
        except Exception as e:
            print(f"❌ Chromium check failed: {e}")
        
        # Create test form data with premium settings
        form_data = {
            'url': 'https://www.airbnb.com/rooms/test',
            'email': 'test@example.com',
            'title': 'Test Listing',
            'description': 'Test description for PDF generation',
            'wants_pdf': True,
            'wants_email': False
        }
        
        print("🧪 Calling optimize_listing with test data...")
        result = optimize_listing(form_data)
        
        print(f"🧪 Result keys: {list(result.keys())}")
        print(f"🧪 PDF download URL: {result.get('pdf_download_url', 'NOT FOUND')}")
        
        return jsonify({
            'success': True,
            'pdf_generated': bool(result.get('pdf_download_url')),
            'pdf_url': result.get('pdf_download_url'),
            'test_data': 'PDF generation test completed',
            'playwright_available': True  # If we get here, import worked
        })
        
    except Exception as e:
        print(f"❌ PDF test error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e),
            'traceback': traceback.format_exc()
        }), 500

@app.route('/debug/wkhtmltopdf', methods=['GET'])
def debug_wkhtmltopdf():
    """Debug endpoint to check wkhtmltopdf installation"""
    import subprocess
    import glob
    
    debug_info = {
        'timestamp': time.time(),
        'system': {}
    }
    
    # Check Heroku and local possible locations for wkhtmltopdf
    possible_paths = [
        '/app/bin/wkhtmltopdf',           # Heroku buildpack location
        '/usr/local/bin/wkhtmltopdf',     # Local development
        '/usr/bin/wkhtmltopdf',           # Local system package
        '/bin/wkhtmltopdf',
        '/opt/wkhtmltopdf/bin/wkhtmltopdf'
    ]
    
    debug_info['path_checks'] = {}
    for path in possible_paths:
        debug_info['path_checks'][path] = os.path.exists(path)
        if os.path.exists(path):
            stat = os.stat(path)
            debug_info['path_checks'][path + '_permissions'] = oct(stat.st_mode)[-3:]
            debug_info['path_checks'][path + '_size'] = stat.st_size
    
    # Legacy check
    wkhtmltopdf_path = '/usr/local/bin/wkhtmltopdf'
    debug_info['wkhtmltopdf_exists'] = os.path.exists(wkhtmltopdf_path)
    
    # Find wkhtmltopdf anywhere on system  
    try:
        result = subprocess.run(['which', 'wkhtmltopdf'], capture_output=True, text=True)
        debug_info['which_wkhtmltopdf'] = result.stdout.strip() if result.returncode == 0 else 'Not found'
    except:
        debug_info['which_wkhtmltopdf'] = 'Command failed'
        
    # Check all bin directories
    try:
        debug_info['usr_bin_contents'] = [f for f in os.listdir('/usr/bin/') if 'wk' in f.lower()][:10]
    except:
        debug_info['usr_bin_contents'] = 'Cannot access'
    
    # Check version if exists
    try:
        result = subprocess.run([wkhtmltopdf_path, '--version'], capture_output=True, text=True, timeout=10)
        debug_info['wkhtmltopdf_version'] = result.stdout.strip() if result.returncode == 0 else result.stderr.strip()
    except Exception as e:
        debug_info['wkhtmltopdf_version'] = str(e)
    
    # Check /usr/local/bin contents
    try:
        debug_info['usr_local_bin_contents'] = os.listdir('/usr/local/bin/')
    except:
        debug_info['usr_local_bin_contents'] = 'Cannot access'
    
    # Check for xvfb (needed for wkhtmltopdf)
    try:
        result = subprocess.run(['which', 'xvfb-run'], capture_output=True, text=True)
        debug_info['xvfb_available'] = result.stdout.strip() if result.returncode == 0 else 'Not found'
    except:
        debug_info['xvfb_available'] = 'Command failed'
    
    # Check Heroku-specific paths
    try:
        debug_info['app_bin_contents'] = [f for f in os.listdir('/app/bin/') if 'wk' in f.lower()][:10] if os.path.exists('/app/bin/') else 'No /app/bin/ directory'
    except:
        debug_info['app_bin_contents'] = 'Cannot access /app/bin/'
    
    return jsonify(debug_info)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5001))
    app.run(host='0.0.0.0', port=port, debug=True) 