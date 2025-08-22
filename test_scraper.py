#!/usr/bin/env python3
"""
Test script for Airbnb image scraping
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.airbnb_scraper import scrape_airbnb_images

def test_image_scraping():
    """Test the image scraping function"""
    
    # Test URL from the logs
    test_url = "https://www.airbnb.co.in/rooms/1270455912817632051?check_in=2025-06-20&check_out=2025-06-22&photo_id=2014343214&source_impression_id=p3_1750316422_P3xqHTFCRnIgKFGR&previous_page_section_name=1000&guests=3&adults=3"
    
    print("🧪 Testing Airbnb Image Scraping")
    print(f"URL: {test_url}")
    print("=" * 80)
    
    try:
        # Test the scraping function
        image_urls = scrape_airbnb_images(test_url, max_images=3)
        
        print("\n" + "=" * 80)
        print("📊 RESULTS:")
        print(f"Total images found: {len(image_urls)}")
        
        if image_urls:
            print("\n🖼️ Found images:")
            for i, url in enumerate(image_urls, 1):
                print(f"  {i}. {url[:100]}...")
        else:
            print("\n❌ No images found")
            
    except Exception as e:
        print(f"\n❌ Error during scraping: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_image_scraping() 