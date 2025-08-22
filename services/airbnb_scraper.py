import requests
from bs4 import BeautifulSoup
import re

def scrape_airbnb_images(url, max_images=3):
    """Scrape images from Airbnb listing"""
    try:
        print(f"=== SCRAPING IMAGES FROM: {url} ===")
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        print(f"Response status: {response.status_code}")
        print(f"Response content length: {len(response.text)}")
        
        soup = BeautifulSoup(response.text, 'html.parser')

        # Debug: Let's see what we're actually getting
        print("🔍 DEBUG: Looking for any img tags...")
        all_imgs = soup.find_all('img')
        print(f"Total img tags found: {len(all_imgs)}")
        
        # Show first few img tags to understand structure
        for i, img in enumerate(all_imgs[:10]):
            src = img.get('src', 'NO_SRC')
            classes = img.get('class', [])
            img_id = img.get('id', 'NO_ID')
            data_uri = img.get('data-original-uri', 'NO_DATA_URI')
            print(f"  IMG {i+1}: src={src[:100]}... classes={classes} id={img_id} data-uri={data_uri[:50] if data_uri != 'NO_DATA_URI' else 'NO_DATA_URI'}...")

        # Also check for picture elements
        pictures = soup.find_all('picture')
        print(f"Total picture elements found: {len(pictures)}")

        image_urls = []
        priority_images = []  # For main hero images
        regular_images = []   # For other images

        # Priority selectors for main hero images (should be captured first)
        priority_selectors = [
            'div[data-plugin-in-point-id="HERO_DEFAULT"] img.i1ezuexe',  # Main hero section images
            'div[data-section-id="HERO_DEFAULT"] img.i1ezuexe',  # Alternative hero section
            'img[id="FMP-target"]',  # Main hero image by ID
            'img[fetchpriority="high"]'  # High priority images (usually main hero)
        ]

        # Regular selectors for other property images
        regular_selectors = [
            'img.i1ezuexe',  # All images with this class
            'picture img',  # Images inside picture elements
            'img[data-original-uri]',
            'img[data-testid*="photo"]',
            'img[src*="airbnb"]',
            'img[src*="muscache"]',  # Add muscache domain
            'div[data-testid="photo-viewer"] img'
        ]

        def extract_image_url(img):
            """Extract and process image URL from img element"""
            src = img.get('src') or img.get('data-original-uri') or img.get('data-src')
            
            if not src:
                return None
                
            # Debug: Show what we found
            if 'airbnb' in src or 'muscache' in src:
                print(f"    🔗 Found potential image URL: {src[:12000]}")
                
                # Check if it has valid image extension
                if any(ext in src for ext in ['.jpg', '.jpeg', '.png', '.webp']):
                    # Skip platform icons and small images, but be more specific
                    if ('platform-assets' in src and ('icons' in src or 'AirbnbPlatformAssets' in src)) or 'im_w=20' in src:
                        print(f"    ❌ Skipping platform/icon image")
                        return None
                    
                    # Skip if it's clearly a property listing image (these are the ones we want!)
                    if '/pictures/miso/Hosting-' in src or '/pictures/hosting/Hosting-' in src:
                        print(f"    ✅ Found property listing image!")
                        # Get high quality version of image
                        if '?im_w=' in src:
                            src = re.sub(r'\?im_w=\d+', '?im_w=1200', src)
                        elif 'w_' in src:
                            src = re.sub(r'w_\d+', 'w_1200', src)
                        return src

                    # For other airbnb/muscache images, still process them but with lower priority
                    if 'platform-assets' not in src:
                        print(f"    ✅ Valid airbnb/muscache image")
                        # Get high quality version of image
                        if '?im_w=' in src:
                            src = re.sub(r'\?im_w=\d+', '?im_w=1200', src)
                        elif 'w_' in src:
                            src = re.sub(r'w_\d+', 'w_1200', src)
                        return src
                    else:
                        print(f"    ❌ Skipping platform asset")
                        return None
                else:
                    print(f"    ❌ No valid image extension found")
            
            return None

        # First, capture priority images (main hero images)
        print("🔍 Searching for priority images...")
        for selector in priority_selectors:
            images = soup.select(selector)
            print(f"  Selector '{selector}': found {len(images)} elements")
            for img in images:
                src = extract_image_url(img)
                if src and src not in priority_images:
                    priority_images.append(src)
                    print(f"✅ Found priority image: {src[:100]}...")

        # Then, capture regular property images
        print("🔍 Searching for regular images...")
        for selector in regular_selectors:
            images = soup.select(selector)
            print(f"  Selector '{selector}': found {len(images)} elements")
            for img in images:
                src = extract_image_url(img)
                if src and src not in priority_images and src not in regular_images:
                    regular_images.append(src)
                    print(f"✅ Found regular image: {src[:100]}...")

        # Combine priority images first, then regular images
        image_urls = priority_images + regular_images
        
        print(f"Total priority images found: {len(priority_images)}")
        print(f"Total regular images found: {len(regular_images)}")
        print(f"Total images found: {len(image_urls)}")
        
        # If we didn't find any images with selectors, try a different approach
        if not image_urls:
            print("🔄 No images found with selectors, trying alternative approach...")
            
            # Extract property ID from URL for targeted search
            property_id = None
            if '/rooms/' in url:
                try:
                    property_id = url.split('/rooms/')[1].split('?')[0]
                    print(f"Property ID extracted: {property_id}")
                except:
                    pass
            
            # Look for any images that might contain the property ID or hosting pattern
            alternative_images = []
            
            # Method 1: Search in img tags
            for img in all_imgs:
                src = img.get('src') or img.get('data-original-uri') or img.get('data-src')
                if src and ('muscache.com' in src or 'airbnb' in src):
                    # Check if it's a property image
                    if property_id and property_id in src:
                        print(f"✅ Found image with property ID: {src[:100]}...")
                        if '?im_w=' in src:
                            src = re.sub(r'\?im_w=\d+', '?im_w=1200', src)
                        alternative_images.append(src)
                    elif '/pictures/miso/Hosting-' in src or '/pictures/hosting/Hosting-' in src:
                        print(f"✅ Found hosting image: {src[:100]}...")
                        if '?im_w=' in src:
                            src = re.sub(r'\?im_w=\d+', '?im_w=1200', src)
                        alternative_images.append(src)
            
            # Method 2: Search entire page source for image URLs
            if not alternative_images and property_id:
                print("🔍 Searching entire page source for image URLs...")
                page_text = response.text
                
                # Look for the specific pattern: pictures/miso/Hosting-{property_id}
                pattern = rf'https://a0\.muscache\.com/im/pictures/miso/Hosting-{property_id}/original/[a-f0-9\-]+\.jpeg'
                found_urls = re.findall(pattern, page_text)
                
                if found_urls:
                    # Remove duplicates while preserving order
                    unique_urls = list(dict.fromkeys(found_urls))
                    print(f"✅ Found {len(found_urls)} image URLs in page source! ({len(unique_urls)} unique)")
                    for img_url in unique_urls:
                        alternative_images.append(img_url)
                        print(f"  Added: {img_url}")
                        if len(alternative_images) >= max_images:
                            break
                else:
                    print("❌ No image URLs found in page source")
                    
                    # Method 3: Try broader search for any muscache image URLs
                    print("🔍 Trying broader search for muscache images...")
                    broad_pattern = r'https://a0\.muscache\.com/im/pictures/[^"\'>\s]+'
                    broad_urls = re.findall(broad_pattern, page_text)
                    
                    for img_url in broad_urls:
                        if property_id in img_url and '.jpeg' in img_url:
                            print(f"✅ Found broad match: {img_url[:100]}...")
                            if '?im_w=' in img_url:
                                img_url = re.sub(r'\?im_w=\d+', '?im_w=1200', img_url)
                            else:
                                img_url = f"{img_url}?im_w=1200"
                            alternative_images.append(img_url)
                            if len(alternative_images) >= max_images:
                                break
            
            image_urls = alternative_images[:max_images]
            print(f"Alternative search found: {len(image_urls)} images")
        
        if image_urls:
            print("Final image URLs found:")
            for i, img_url in enumerate(image_urls[:3]):
                print(f"  {i+1}: {img_url[:150]}...")
        else:
            print("❌ No images found with any method")
            
        return image_urls[:max_images]
    except Exception as e:
        print(f"Error scraping images: {e}")
        return [] 