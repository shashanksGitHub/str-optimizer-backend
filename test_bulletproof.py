#!/usr/bin/env python3
"""
BULLETPROOF PDF TEST - Verify the solution before deployment
"""

import subprocess
import os
import tempfile

def test_docker_build():
    """Test the Docker build process"""
    print("🧪 TESTING BULLETPROOF DOCKER BUILD...")
    
    try:
        # Build the Docker image
        print("🔨 Building Docker image...")
        build_cmd = ["docker", "build", "-t", "bulletproof-pdf-test", "."]
        
        result = subprocess.run(
            build_cmd, 
            capture_output=True, 
            text=True, 
            timeout=300,  # 5 minute timeout
            cwd=os.path.dirname(__file__)
        )
        
        if result.returncode == 0:
            print("✅ Docker build successful!")
            print("📋 Build completed - wkhtmltopdf should be installed and verified")
            return True
        else:
            print("❌ Docker build failed:")
            print(f"STDERR: {result.stderr}")
            print(f"STDOUT: {result.stdout}")
            return False
            
    except subprocess.TimeoutExpired:
        print("❌ Docker build timed out (>5 minutes)")
        return False
    except Exception as e:
        print(f"❌ Docker build error: {e}")
        return False

def test_pdf_generation():
    """Test PDF generation inside the container"""
    print("🧪 TESTING PDF GENERATION IN CONTAINER...")
    
    try:
        # Test command to run inside container
        test_cmd = [
            "docker", "run", "--rm",
            "-v", f"{os.path.dirname(__file__)}:/test",
            "bulletproof-pdf-test",
            "python3", "-c", """
import sys
sys.path.append('/app')
from services.html_pdf_generator import generate_html_pdf

# Test data
test_data = {
    'property_title': 'Test Property - PDF Generation Verification',
    'property_rating': '4.98',
    'property_location': 'Test Location',
    'optimization_summary': 'This is a bulletproof PDF generation test.',
    'recommendations': [
        {
            'title': 'Test Recommendation',
            'priority': 'HIGH PRIORITY',
            'content': 'This verifies that PDF generation is working perfectly.'
        }
    ]
}

# Generate PDF
result = generate_html_pdf(test_data, '/tmp/bulletproof_test.pdf')

if result:
    print('🎉 BULLETPROOF PDF TEST SUCCESSFUL!')
    import os
    if os.path.exists('/tmp/bulletproof_test.pdf'):
        size = os.path.getsize('/tmp/bulletproof_test.pdf')
        print(f'📄 PDF Size: {size:,} bytes')
        if size > 10000:
            print('✅ PDF SIZE VERIFICATION PASSED')
            sys.exit(0)
        else:
            print('❌ PDF TOO SMALL')
            sys.exit(1)
    else:
        print('❌ PDF NOT CREATED')
        sys.exit(1)
else:
    print('❌ BULLETPROOF PDF TEST FAILED!')
    sys.exit(1)
"""
        ]
        
        result = subprocess.run(
            test_cmd,
            capture_output=True,
            text=True,
            timeout=120  # 2 minute timeout
        )
        
        if result.returncode == 0:
            print("✅ Container PDF generation test successful!")
            print(f"OUTPUT: {result.stdout}")
            return True
        else:
            print("❌ Container PDF generation test failed:")
            print(f"STDERR: {result.stderr}")
            print(f"STDOUT: {result.stdout}")
            return False
            
    except subprocess.TimeoutExpired:
        print("❌ PDF generation test timed out")
        return False
    except Exception as e:
        print(f"❌ PDF generation test error: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 BULLETPROOF PDF SOLUTION - COMPREHENSIVE TESTING")
    print("=" * 60)
    
    # Test 1: Docker Build
    print("\n📦 TEST 1: Docker Build Verification")
    build_success = test_docker_build()
    
    if not build_success:
        print("❌ Build test failed - cannot proceed")
        return False
    
    # Test 2: PDF Generation
    print("\n📄 TEST 2: PDF Generation Verification") 
    pdf_success = test_pdf_generation()
    
    if not pdf_success:
        print("❌ PDF generation test failed")
        return False
    
    print("\n🎉 ALL TESTS PASSED - BULLETPROOF SOLUTION VERIFIED!")
    print("✅ Ready for production deployment")
    return True

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1) 