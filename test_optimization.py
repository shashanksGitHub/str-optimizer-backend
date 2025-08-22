#!/usr/bin/env python3
"""
Test script for complete optimization process
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.str_optimizer import optimize_listing

def test_optimization():
    """Test the complete optimization process"""
    
    # Test data
    test_data = {
        'listingUrl': "https://www.airbnb.co.in/rooms/1270455912817632051?check_in=2025-06-20&check_out=2025-06-22&photo_id=2014343214&source_impression_id=p3_1750316422_P3xqHTFCRnIgKFGR&previous_page_section_name=1000&guests=3&adults=3",
        'email': 'test@example.com',
        'title': 'Rental unit in Benaulim · ★4.81 · 1 bedroom · 1 bed · 1 bathroom',
        'description': 'Studio @Costa Montage Benaulim',
        'wants_pdf': True,
        'wants_email': False  # Don't send email during test
    }
    
    print("🧪 Testing Complete Optimization Process")
    print("=" * 80)
    
    try:
        # Run optimization
        result = optimize_listing(test_data)
        
        print("\n" + "=" * 80)
        print("📊 OPTIMIZATION RESULTS:")
        print(f"✅ Optimized Title: {result.get('optimized_title', 'N/A')}")
        print(f"✅ Image Count: {result.get('image_count', 0)}")
        print(f"✅ PDF Generated: {'Yes' if result.get('pdf_download_url') else 'No'}")
        
        if result.get('image_urls'):
            print(f"\n🖼️ Images Found ({len(result['image_urls'])}):")
            for i, url in enumerate(result['image_urls'][:3], 1):
                print(f"  {i}. {url[:80]}...")
        else:
            print("\n❌ No images found")
            
        if result.get('pdf_download_url'):
            print(f"\n📄 PDF Download URL: {result['pdf_download_url']}")
            
    except Exception as e:
        print(f"\n❌ Error during optimization: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_optimization() 