import os
import requests
from bs4 import BeautifulSoup
from openai import OpenAI
from .airbnb_scraper import scrape_airbnb_images
from .pdf_generator import generate_professional_pdf
from .email_service import send_email
import tempfile
import json
import random
from datetime import datetime, timedelta
import uuid
import urllib.parse

# Initialize OpenAI client - handle missing API key gracefully
def get_openai_client():
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("Warning: OPENAI_API_KEY not set. AI features will be limited.")
        return None
    try:
        return OpenAI(api_key=api_key)
    except Exception as e:
        print(f"Warning: Could not initialize OpenAI client: {e}")
        return None

client = get_openai_client()

def generate_mock_trend_data():
    """Generate realistic mock data for occupancy and revenue trends"""
    months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    base_occupancy = 65
    base_revenue = 150  # USD monthly revenue
    
    occupancy_data = []
    revenue_data = []
    
    for i, month in enumerate(months):
        # Simulate seasonal patterns (higher in summer/winter holidays)
        seasonal_factor = 1.0
        if month in ['Jun', 'Jul', 'Aug', 'Dec']:  # Peak seasons
            seasonal_factor = 1.3
        elif month in ['Jan', 'Feb', 'Sep']:  # Low seasons
            seasonal_factor = 0.8
        
        # Add some randomness
        random_factor = random.uniform(0.9, 1.1)
        
        occupancy = min(95, int(base_occupancy * seasonal_factor * random_factor))
        revenue = int(base_revenue * seasonal_factor * random_factor)
        
        occupancy_data.append({'month': month, 'value': occupancy})
        revenue_data.append({'month': month, 'value': revenue})
    
    return occupancy_data, revenue_data

def extract_location_from_url_and_content(url, title="", description=""):
    """Extract location from Airbnb URL and listing content using multiple strategies"""
    location = None
    city = None
    country = None
    
    if not url:
        return None, None, None
    
    try:
        # Strategy 1: Parse URL structure
        # Airbnb URLs often contain location info: airbnb.com/rooms/12345?location=city-country
        parsed_url = urllib.parse.urlparse(url.lower())
        
        # Check query parameters for location
        query_params = urllib.parse.parse_qs(parsed_url.query)
        if 'location' in query_params:
            location_param = query_params['location'][0]
            if location_param:
                location = location_param.replace('-', ' ').title()
        
        # Strategy 2: Extract from URL path patterns
        # Look for common city names in URL
        url_lower = url.lower()
        
        # Major global cities that commonly appear in URLs
        global_cities = {
            'new-york': 'New York, USA',
            'newyork': 'New York, USA', 
            'los-angeles': 'Los Angeles, USA',
            'losangeles': 'Los Angeles, USA',
            'san-francisco': 'San Francisco, USA',
            'sanfrancisco': 'San Francisco, USA',
            'miami': 'Miami, USA',
            'chicago': 'Chicago, USA',
            'boston': 'Boston, USA',
            'seattle': 'Seattle, USA',
            'austin': 'Austin, USA',
            'denver': 'Denver, USA',
            'atlanta': 'Atlanta, USA',
            'nashville': 'Nashville, USA',
            'portland': 'Portland, USA',
            'washington': 'Washington DC, USA',
            'philadelphia': 'Philadelphia, USA',
            'london': 'London, UK',
            'paris': 'Paris, France',
            'rome': 'Rome, Italy',
            'barcelona': 'Barcelona, Spain',
            'madrid': 'Madrid, Spain',
            'amsterdam': 'Amsterdam, Netherlands',
            'berlin': 'Berlin, Germany',
            'munich': 'Munich, Germany',
            'vienna': 'Vienna, Austria',
            'prague': 'Prague, Czech Republic',
            'budapest': 'Budapest, Hungary',
            'lisbon': 'Lisbon, Portugal',
            'dublin': 'Dublin, Ireland',
            'copenhagen': 'Copenhagen, Denmark',
            'stockholm': 'Stockholm, Sweden',
            'oslo': 'Oslo, Norway',
            'helsinki': 'Helsinki, Finland',
            'tokyo': 'Tokyo, Japan',
            'kyoto': 'Kyoto, Japan',
            'osaka': 'Osaka, Japan',
            'seoul': 'Seoul, South Korea',
            'singapore': 'Singapore',
            'hong-kong': 'Hong Kong',
            'hongkong': 'Hong Kong',
            'bangkok': 'Bangkok, Thailand',
            'mumbai': 'Mumbai, India',
            'delhi': 'Delhi, India',
            'bangalore': 'Bangalore, India',
            'goa': 'Goa, India',
            'benaulim': 'Benaulim, Goa, India',
            'sydney': 'Sydney, Australia',
            'melbourne': 'Melbourne, Australia',
            'toronto': 'Toronto, Canada',
            'vancouver': 'Vancouver, Canada',
            'montreal': 'Montreal, Canada',
            'mexico-city': 'Mexico City, Mexico',
            'cancun': 'Cancun, Mexico',
            'rio-de-janeiro': 'Rio de Janeiro, Brazil',
            'sao-paulo': 'São Paulo, Brazil',
            'buenos-aires': 'Buenos Aires, Argentina',
            'lima': 'Lima, Peru',
            'cape-town': 'Cape Town, South Africa',
            'dubai': 'Dubai, UAE',
            'istanbul': 'Istanbul, Turkey',
            'tel-aviv': 'Tel Aviv, Israel',
            'cairo': 'Cairo, Egypt'
        }
        
        for city_key, full_location in global_cities.items():
            if city_key in url_lower:
                location = full_location
                city = full_location.split(',')[0].strip()
                if ',' in full_location:
                    country = full_location.split(',')[-1].strip()
                break
        
        # Strategy 3: Use AI to extract location from title and description
        if not location and (title or description):
            client = get_openai_client()
            if client:
                try:
                    location_prompt = f"""Extract the location (city, neighborhood, or area) from this Airbnb listing information. Return ONLY the location in format "City, Country" or "Neighborhood, City, Country". If no clear location is found, return "Unknown Location".

Title: {title}
Description: {description[:500]}
URL: {url}

Examples of good responses:
- "Manhattan, New York, USA"
- "Trastevere, Rome, Italy" 
- "Shibuya, Tokyo, Japan"
- "South Beach, Miami, USA"
- "Unknown Location" (if no location found)

Return only the location, nothing else."""
                    
                    location_response = client.chat.completions.create(
                        model="gpt-3.5-turbo",
                        messages=[
                            {"role": "system", "content": "You are a location extraction expert. Extract locations from text with high accuracy."},
                            {"role": "user", "content": location_prompt}
                        ]
                    )
                    ai_location = location_response.choices[0].message.content.strip()
                    
                    if ai_location and ai_location != "Unknown Location" and len(ai_location) > 3:
                        location = ai_location
                        if ',' in ai_location:
                            parts = [part.strip() for part in ai_location.split(',')]
                            city = parts[0] if len(parts) > 0 else None
                            country = parts[-1] if len(parts) > 1 else None
                        else:
                            city = ai_location
                            
                except Exception as e:
                    print(f"AI location extraction failed: {e}")
        
        # Strategy 4: Final fallback - try to scrape from the actual page
        if not location:
            try:
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
                }
                response = requests.get(url, headers=headers, timeout=10)
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Look for location in meta tags
                location_meta = soup.find('meta', property='og:locality')
                if location_meta and location_meta.get('content'):
                    city = location_meta['content']
                
                country_meta = soup.find('meta', property='og:country-name')
                if country_meta and country_meta.get('content'):
                    country = country_meta['content']
                
                if city and country:
                    location = f"{city}, {country}"
                elif city:
                    location = city
                    
            except Exception as e:
                print(f"Page scraping for location failed: {e}")
    
    except Exception as e:
        print(f"Location extraction error: {e}")
    
    return location, city, country

def generate_competitor_pricing_data(location, property_type):
    """Generate realistic competitor pricing comparison data based on actual location"""
    # Dynamic base prices based on location type and global markets
    base_price = 80  # USD per night baseline
    location_multiplier = 1.0
    
    if location:
        location_lower = location.lower()
        
        # Major expensive cities
        if any(city in location_lower for city in ['new york', 'manhattan', 'san francisco', 'london', 'paris', 'tokyo', 'singapore', 'hong kong', 'sydney', 'zurich']):
            location_multiplier = 2.5
        elif any(city in location_lower for city in ['los angeles', 'miami', 'chicago', 'boston', 'seattle', 'rome', 'barcelona', 'amsterdam', 'toronto', 'dubai']):
            location_multiplier = 2.0
        elif any(city in location_lower for city in ['austin', 'denver', 'atlanta', 'madrid', 'berlin', 'melbourne', 'vancouver']):
            location_multiplier = 1.5
        elif any(country in location_lower for country in ['usa', 'uk', 'france', 'germany', 'australia', 'canada', 'japan']):
            location_multiplier = 1.3
        elif any(region in location_lower for region in ['europe', 'asia', 'north america']):
            location_multiplier = 1.2
        else:
            # Developing markets or smaller cities
            location_multiplier = 1.0
    
    # Property type multipliers
    property_multipliers = {
        'villa': 1.8,
        'house': 1.4,
        'penthouse': 2.2,
        'apartment': 1.0,
        'studio': 0.7,
        'loft': 1.3,
        'condo': 1.1,
        'townhouse': 1.2
    }
    
    # Find property type multiplier
    property_multiplier = 1.0
    if property_type:
        property_lower = property_type.lower()
        for prop_type, multiplier in property_multipliers.items():
            if prop_type in property_lower:
                property_multiplier = multiplier
                break
    
    # Calculate base price for the area
    area_base_price = int(base_price * location_multiplier * property_multiplier)
    
    # Generate competitor data
    competitors = []
    
    for i in range(5):
        competitor_price = int(area_base_price * random.uniform(0.75, 1.4))
        competitors.append({
            'name': f'Similar Property {i+1}',
            'price': competitor_price,
            'bedrooms': random.choice([1, 2, 3, 4]),
            'rating': round(random.uniform(4.0, 4.9), 1)
        })
    
    # Add user's property
    competitors.append({
        'name': 'Your Property',
        'price': area_base_price,
        'bedrooms': 2,  # Default
        'rating': 4.5,  # Default
        'isYours': True
    })
    
    return sorted(competitors, key=lambda x: x['price'])

def optimize_listing(form_data):
    """Main optimization function that processes STR listing data"""
    # Handle both 'url' and 'listingUrl' keys from frontend
    url = form_data.get('url') or form_data.get('listingUrl')
    title = form_data.get('title')
    description = form_data.get('description')
    email = form_data.get('email')
    reviews = form_data.get('reviews', '')
    wants_pdf = form_data.get('wants_pdf', False)
    wants_email = form_data.get('wants_email', False)
    image_url = form_data.get('image_url')

    print(f"🔍 Processing optimization request:")
    print(f"  URL: {url}")
    print(f"  Title: {title}")
    print(f"  Description: {description[:100] if description else 'None'}...")
    print(f"  Email: {email}")

    # Get description from URL if not provided manually
    if not description and url:
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1'
            }
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()

            if 'text/html' not in response.headers.get('content-type', ''):
                raise Exception('URL does not return HTML content')

            soup = BeautifulSoup(response.text, 'html.parser')
            title_tag = soup.find('meta', property='og:title')
            desc_tag = soup.find('meta', property='og:description')

            if not title and title_tag:
                title = title_tag['content']
            if not description and desc_tag:
                description = desc_tag['content']

        except Exception as e:
            raise Exception(f'Failed to scrape URL: {str(e)}')

    if not description:
        raise Exception('No description provided or found')

    # Extract location dynamically from URL and content
    location, city, country = extract_location_from_url_and_content(url, title, description)
    
    # If no location detected, use generic terms
    if not location:
        location = "your area"
        city = "your city"
        country = "your country"
    
    print(f"📍 Detected location: {location}")

    # Generate optimized title and description with enhanced prompts
    title_prompt = (
        f"Create 3 compelling Airbnb titles that maximize bookings. Follow these guidelines:\n"
        f"- Aim for 50 characters or less (Airbnb recommendation), but prioritize impact over strict length\n"
        f"- Include location/neighborhood if mentioned\n"
        f"- Highlight unique features or amenities\n"
        f"- Use power words that attract guests\n"
        f"- Make them searchable and descriptive\n"
        f"- Each title should have a different approach/focus\n\n"
        f"Original listing info: {description}\n\n"
        f"Return exactly 3 titles, each on a separate line, numbered 1-3. Example format:\n"
        f"1. First title option here\n"
        f"2. Second title option here\n"
        f"3. Third title option here"
    )

    description_prompt = (
        f"Create a compelling 2-3 line summary for this Airbnb property that will be used as an 'AI Analysis Summary':\n"
        f"- Maximum 2-3 sentences only\n"
        f"- Start with the key appeal/hook\n"
        f"- Mention the location and main features\n"
        f"- Use engaging, descriptive language\n"
        f"- NO call-to-action needed\n"
        f"- Keep it concise and impactful\n\n"
        f"Property details: {description}\n"
        f"Location: {location}\n\n"
        f"Return only the 2-3 line summary, nothing else."
    )

    # Generate optimized titles (3 options)
    title_suggestions = []
    if client:
        title_response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are an expert Airbnb title optimizer who creates high-converting listing titles with different strategic approaches."},
                {"role": "user", "content": title_prompt}
            ]
        )
        title_response_text = title_response.choices[0].message.content.strip()
        
        # Parse the numbered list response
        lines = title_response_text.split('\n')
        for line in lines:
            line = line.strip()
            if line and (line.startswith(('1.', '2.', '3.')) or line.startswith(('1)', '2)', '3)'))):
                # Remove the number prefix and clean up
                title = line.split('.', 1)[-1].split(')', 1)[-1].strip()
                if title:
                    # Keep full title - let users see complete suggestions
                    title_suggestions.append(title)
        
        # Fallback if parsing failed - create 3 variations
        if len(title_suggestions) < 3:
            title_suggestions = [
                "★ Beautiful Property | Perfect Location",
                "🏡 Stunning Home | Great Amenities",
                "✨ Cozy Retreat | Prime Location"
            ]
    else:
        title_suggestions = [
            "★ Beautiful Property | Perfect Location",
            "🏡 Stunning Home | Great Amenities", 
            "✨ Cozy Retreat | Prime Location"
        ]
    
    # Keep the first title as optimized_title for backward compatibility
    optimized_title = title_suggestions[0] if title_suggestions else "★ Beautiful Property | Perfect Location"

    # Generate optimized description
    if client:
        desc_response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are an expert Airbnb listing optimizer who writes compelling descriptions that convert browsers into bookers."},
                {"role": "user", "content": description_prompt}
            ]
        )
        optimized_description = desc_response.choices[0].message.content.strip()
    else:
        optimized_description = f"Discover comfort and style at this exceptional property in {location}. Featuring modern amenities and thoughtful design for the perfect getaway."

    # Suggest amenities
    if client:
        amenities_prompt = f"Suggest exactly 5 missing amenities that would improve this Airbnb listing: {description}. Format your response with each amenity on its own line like this:\n1. First amenity\n2. Second amenity\n3. Third amenity\n4. Fourth amenity\n5. Fifth amenity"
        amenities_response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are an Airbnb amenity expert."},
                {"role": "user", "content": amenities_prompt}
            ]
        )
        amenities = amenities_response.choices[0].message.content.strip()
    else:
        amenities = """1. High-speed WiFi for remote work
2. Smart TV with streaming services
3. Coffee machine with premium coffee
4. Air conditioning/heating system
5. In-unit washer and dryer"""

    # ENHANCED: Detailed Review Sentiment Analysis
    review_sentiment_analysis = ""
    if reviews and client:
        sentiment_prompt = f"""Analyze these Airbnb reviews for detailed sentiment insights:

Reviews: {reviews}

Provide analysis in exactly this format:
**Recurring Praise:**
- [Top 3 most mentioned positive aspects]

**Common Complaints:**
- [Top 2-3 recurring issues mentioned]

**Sentiment Trends:**
- Overall sentiment: [Positive/Mixed/Negative] ([X]% positive mentions)
- Guest satisfaction score: [X]/10
- Key emotional drivers: [list top 2-3]

**Actionable Insights:**
- [2-3 specific recommendations based on feedback patterns]"""
        
        try:
            sentiment_response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are an expert review sentiment analyst specializing in hospitality feedback analysis."},
                    {"role": "user", "content": sentiment_prompt}
                ]
            )
            review_sentiment_analysis = sentiment_response.choices[0].message.content.strip()
        except Exception as e:
            print(f"Sentiment analysis error: {e}")
    
    if not review_sentiment_analysis:
        review_sentiment_analysis = """**Recurring Praise:**
- Location and accessibility
- Cleanliness and comfort
- Host responsiveness

**Common Complaints:**
- WiFi connectivity issues
- Noise from nearby areas

**Sentiment Trends:**
- Overall sentiment: Positive (78% positive mentions)
- Guest satisfaction score: 7.8/10
- Key emotional drivers: Comfort, convenience, value

**Actionable Insights:**
- Upgrade internet infrastructure for better connectivity
- Add noise-canceling features or soundproofing
- Highlight location benefits more prominently in listing"""

    # NEW: Booking Gap & Occupancy Optimization Analysis
    booking_gap_analysis = ""
    if client:
        gap_prompt = f"""Analyze booking optimization opportunities for this Airbnb property:

Property: {title}
Location: {url}
Description: {description[:200]}

Provide analysis in exactly this format:
**Calendar Gap Analysis:**
- Identified low-demand periods: [specific days/periods]
- Average booking gap length: [X] days

**Occupancy Optimization Strategies:**
- Minimum stay adjustments: [specific recommendations]
- Midweek discount opportunities: [X]% discount suggested
- Last-minute booking incentives: [specific strategies]

**Revenue Recovery Tactics:**
- Monthly stay discounts: [X]% for 28+ days
- Seasonal pricing adjustments: [specific recommendations]
- Gap-filling promotions: [2-3 specific strategies]"""
        
        try:
            gap_response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are an Airbnb revenue optimization specialist focusing on occupancy maximization."},
                    {"role": "user", "content": gap_prompt}
                ]
            )
            booking_gap_analysis = gap_response.choices[0].message.content.strip()
        except Exception as e:
            print(f"Booking gap analysis error: {e}")
    
    if not booking_gap_analysis:
        booking_gap_analysis = """**Calendar Gap Analysis:**
- Identified low-demand periods: Weekdays (Mon-Thu), mid-month periods
- Average booking gap length: 3-4 days

**Occupancy Optimization Strategies:**
- Minimum stay adjustments: Reduce to 2 nights for weekdays
- Midweek discount opportunities: 15% discount suggested for Mon-Thu
- Last-minute booking incentives: 10% discount for bookings within 7 days

**Revenue Recovery Tactics:**
- Monthly stay discounts: 25% for 28+ days
- Seasonal pricing adjustments: Increase rates 20% for peak season, decrease 15% for off-season
- Gap-filling promotions: Flash sales, extended stay packages, early bird discounts"""

    # NEW: Guest Profile Match Analysis
    guest_profile_analysis = ""
    if client:
        profile_prompt = f"""Analyze the ideal guest profile for this Airbnb property:

Property: {title}
Description: {description}
Location context: {url}
Reviews available: {'Yes' if reviews else 'No'}

Provide analysis in exactly this format:
**Primary Guest Personas:**
1. [Persona 1]: [description, % of bookings]
2. [Persona 2]: [description, % of bookings]  
3. [Persona 3]: [description, % of bookings]

**Guest Demographics:**
- Age range: [X-Y] years (primary), [X-Y] years (secondary)
- Travel purpose: [leisure/business/mixed] ([X]% split)
- Group size: [X] people average
- Booking lead time: [X] days average

**Tailored Recommendations:**
- Amenities to emphasize: [top 3 for target guests]
- Messaging adjustments: [2-3 specific suggestions]
- Service enhancements: [2-3 guest-specific improvements]"""
        
        try:
            profile_response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a guest persona analyst specializing in short-term rental market segmentation."},
                    {"role": "user", "content": profile_prompt}
                ]
            )
            guest_profile_analysis = profile_response.choices[0].message.content.strip()
        except Exception as e:
            print(f"Guest profile analysis error: {e}")
    
    if not guest_profile_analysis:
        guest_profile_analysis = """**Primary Guest Personas:**
1. Leisure Couples: Romantic getaways, weekend trips (40% of bookings)
2. Remote Workers: Digital nomads, extended stays (35% of bookings)
3. Small Families: Parents with 1-2 children, vacation stays (25% of bookings)

**Guest Demographics:**
- Age range: 28-45 years (primary), 25-35 years (secondary)
- Travel purpose: Leisure (60%), Business (25%), Mixed (15%)
- Group size: 2.3 people average
- Booking lead time: 12 days average

**Tailored Recommendations:**
- Amenities to emphasize: High-speed WiFi, romantic ambiance features, family-friendly amenities
- Messaging adjustments: Highlight work-from-home setup, romantic features, child safety measures
- Service enhancements: Welcome packages for couples, workspace setup guide, family activity recommendations"""

    # Scrape images from Airbnb listing
    image_urls = []
    if url:
        print(f"🖼️ Starting image scraping for URL: {url}")
        try:
            image_urls = scrape_airbnb_images(url, max_images=3)
            print(f"🖼️ Image scraping completed. Found {len(image_urls)} images")
            if image_urls:
                print(f"🖼️ First few image URLs: {image_urls[:2]}")
            else:
                print("🖼️ No images found during scraping")
        except Exception as e:
            print(f"❌ Image scraping failed: {e}")
            image_urls = []
    else:
        print("🖼️ No URL provided, skipping image scraping")

    # Enhanced Analytics: Competitor Pricing Analysis
    pricing_analysis = ""
    try:
        pricing_prompt = f"""Analyze pricing for a {title} in {location}. Provide exactly 3 concise points:
1. Market rate range for similar properties
2. Seasonal pricing strategy (high/low season rates)
3. One key revenue optimization tip
Keep each point to 1-2 sentences maximum."""
        
        pricing_response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": f"You are an Airbnb pricing strategist with expertise in global vacation rental markets. Focus on {location if location != 'your area' else 'local market'} dynamics."},
                {"role": "user", "content": pricing_prompt}
            ]
        )
        pricing_analysis = pricing_response.choices[0].message.content.strip()
    except Exception as e:
        print(f"Pricing analysis error: {e}")
        pricing_analysis = f"Pricing analysis unavailable. Consider researching similar properties in {location if location != 'your area' else 'your local area'} for competitive rates."

    # Enhanced Analytics: Photo Quality Audit
    photo_audit = ""
    try:
        if image_urls:
            photo_count = len(image_urls)
            photo_prompt = f"""Analyze this Airbnb listing's photo strategy:
- Total photos: {photo_count}
- Property type: {title}
- Location: {location}

Provide exactly 3 concise recommendations:
1. Top missing photo type needed
2. One lighting/quality improvement
3. One key shot to boost bookings
Keep each point to 1-2 sentences maximum."""
            
            photo_response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are an Airbnb photography expert specializing in listing optimization."},
                    {"role": "user", "content": photo_prompt}
                ]
            )
            photo_audit = photo_response.choices[0].message.content.strip()
        else:
            photo_audit = "No photos detected. Professional photos are essential - consider hiring a photographer to showcase your property's best features."
    except Exception as e:
        print(f"Photo audit error: {e}")
        photo_audit = "Photo audit unavailable. Ensure your listing has high-quality photos of all key areas."

    # Enhanced Analytics: Performance Insights & Optimization Potential
    performance_insights = ""
    try:
        amenities_count = len(amenities.split('\n'))
        insights_prompt = f"""Based on this Airbnb listing optimization:
- Original title: {title}
- Optimized title: {optimized_title}
- Location: {location}
- Amenities added: {amenities_count} new suggestions

Provide exactly 3 concise insights:
1. Expected booking improvement % and revenue impact
2. Top 2 performance drivers identified
3. Market positioning advantage gained
Keep each point to 1-2 sentences maximum."""
        
        insights_response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are an Airbnb performance analyst with expertise in listing optimization ROI."},
                {"role": "user", "content": insights_prompt}
            ]
        )
        performance_insights = insights_response.choices[0].message.content.strip()
    except Exception as e:
        print(f"Performance insights error: {e}")
        performance_insights = "Performance analysis unavailable. Track your booking metrics after implementing these optimizations."

    # Generate dynamic market analysis data
    market_analysis_data = generate_dynamic_market_data(client, location, title, description)
    competitive_scores = generate_competitive_scores(client, location, title, description)
    revenue_projections = generate_revenue_projections(client, location, title)
    dynamic_percentages = generate_dynamic_percentages(client, title, description)
    
    # Generate chart data for visualizations
    occupancy_trend_data, revenue_trend_data = generate_mock_trend_data()
    competitor_pricing_data = generate_competitor_pricing_data(location, title)

    # Create PDF if requested
    pdf_path = None
    if wants_pdf:
        try:
            print("📄 Generating professional PDF report...")
            
            # Create PDF with a more predictable filename
            pdf_filename = f"str_report_{uuid.uuid4().hex[:12]}.pdf"
            pdf_path = os.path.join(tempfile.gettempdir(), pdf_filename)
            
            # Prepare optimization data for the professional PDF
            optimization_data = {
                'title': title,
                'description': description,
                'location': location,
                'title_suggestions': title_suggestions,
                'optimized_description': optimized_description,
                'amenities': amenities,
                'review_sentiment_analysis': review_sentiment_analysis,
                'booking_gap_analysis': booking_gap_analysis,
                'guest_profile_analysis': guest_profile_analysis,
                'pricing_analysis': pricing_analysis,
                'photo_audit': photo_audit,
                'performance_insights': performance_insights,
                'image_urls': image_urls,
                'market_analysis_data': market_analysis_data,
                'competitive_scores': competitive_scores,
                'revenue_projections': revenue_projections,
                'dynamic_percentages': dynamic_percentages
            }
            
            # Generate the professional PDF
            success = generate_professional_pdf(optimization_data, pdf_path)
            
            if success and os.path.exists(pdf_path) and os.path.getsize(pdf_path) > 0:
                print(f"✅ Professional PDF generated successfully: {os.path.getsize(pdf_path)} bytes")
            else:
                print(f"❌ Professional PDF generation failed")
                pdf_path = None

        except Exception as e:
            print(f"PDF generation error: {e}")
            pdf_path = None

    print("📧 Checking email sending...")
    # Send email if requested
    # Re-enabled with improved error handling
    DISABLE_EMAIL_FOR_DEBUG = False
    if wants_email and email and not DISABLE_EMAIL_FOR_DEBUG:
        try:
            print(f"📧 Sending email to: {email}")
            email_result = send_email(email, optimized_description, amenities, review_sentiment_analysis, pdf_path)
            if email_result is not False:
                print("✅ Email sent successfully")
            else:
                print("⚠️ Email sending failed but continuing...")
        except Exception as e:
            print(f"❌ Email sending exception: {e} - continuing anyway...")
    else:
        if DISABLE_EMAIL_FOR_DEBUG:
            print("📧 Email temporarily disabled for debugging")
        else:
            print("📧 Email not requested or no email provided")

    print("📋 Building result dictionary...")
    result = {
        'optimized_title': optimized_title,
        'title_suggestions': title_suggestions,  # NEW - Array of 3 title options
        'optimized_description': optimized_description,
        'suggested_amenities': amenities,
        'review_summary': review_sentiment_analysis,  # Enhanced sentiment analysis
        'booking_gap_analysis': booking_gap_analysis,  # NEW
        'guest_profile_analysis': guest_profile_analysis,  # NEW
        'pricing_analysis': pricing_analysis,
        'photo_audit': photo_audit,
        'performance_insights': performance_insights,
        'occupancy_trend_data': occupancy_trend_data,  # NEW - Chart data
        'revenue_trend_data': revenue_trend_data,  # NEW - Chart data
        'competitor_pricing_data': competitor_pricing_data,  # NEW - Chart data
        'image_urls': image_urls,
        'image_count': len(image_urls)
    }
    
    print("📄 Adding PDF download URL to result...")
    if pdf_path and os.path.exists(pdf_path):
        pdf_filename = os.path.basename(pdf_path)
        result['pdf_download_url'] = f"/api/download/{pdf_filename}"
        print(f"✅ PDF download URL: {result['pdf_download_url']}")
        print(f"✅ PDF file location: {pdf_path}")
    else:
        print("❌ No PDF path available or file doesn't exist")
    
    print("✅ Returning optimization result...")
    return result


def generate_dynamic_market_data(client, location, title, description):
    """Generate AI-powered market analysis data"""
    if not client:
        return None
    
    try:
        market_prompt = f"""Analyze the short-term rental market for this property:
Location: {location}
Title: {title}
Description: {description}

Generate realistic market data in this JSON format:
{{
    "price_range_min": [number],
    "price_range_max": [number], 
    "currency": "[currency code]",
    "market_insights": [
        "[insight 1 about market rates]",
        "[insight 2 about pricing strategy]", 
        "[insight 3 about revenue optimization]"
    ]
}}

Base pricing on local market conditions and property type."""
        
        market_response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a short-term rental market analyst. Provide realistic pricing data based on location and property type."},
                {"role": "user", "content": market_prompt}
            ]
        )
        
        import json
        market_data = json.loads(market_response.choices[0].message.content.strip())
        return market_data
        
    except Exception as e:
        print(f"Market data generation error: {e}")
        return None


def generate_competitive_scores(client, location, title, description):
    """Generate AI-powered competitive advantage scores"""
    if not client:
        return None
    
    try:
        scores_prompt = f"""Analyze this property's competitive advantages:
Location: {location}
Title: {title}
Description: {description}

Rate each category from 1-100 based on market competitiveness:
- Market Positioning: How well positioned vs competitors
- Amenity Score: Quality/uniqueness of amenities
- Visual Score: Likely photo/presentation quality
- Experience Score: Overall guest experience potential

Respond in JSON format:
{{
    "market_positioning": [1-100],
    "amenity_score": [1-100],
    "visual_score": [1-100],
    "experience_score": [1-100]
}}"""
        
        scores_response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a competitive analysis expert for short-term rentals."},
                {"role": "user", "content": scores_prompt}
            ]
        )
        
        import json
        scores_data = json.loads(scores_response.choices[0].message.content.strip())
        return scores_data
        
    except Exception as e:
        print(f"Competitive scores generation error: {e}")
        return None


def generate_revenue_projections(client, location, title):
    """Generate AI-powered revenue projections and booking statistics"""
    if not client:
        return None
    
    try:
        revenue_prompt = f"""Generate revenue projections for this property:
Location: {location}
Title: {title}

Provide realistic projections in JSON format:
{{
    "booking_improvement": [5-40 percent],
    "revenue_impact": [5-30 percent],
    "occupancy_rates": [[leisure %], [family %], [business %]],
    "seasonal_adjustments": {{
        "peak_increase": [10-60 percent],
        "off_season_decrease": [10-40 percent], 
        "weekend_premium": [15-50 percent]
    }}
}}

Base on location market conditions and property type."""
        
        revenue_response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a revenue management expert for vacation rentals."},
                {"role": "user", "content": revenue_prompt}
            ]
        )
        
        import json
        revenue_data = json.loads(revenue_response.choices[0].message.content.strip())
        return revenue_data
        
    except Exception as e:
        print(f"Revenue projections generation error: {e}")
        return None


def generate_dynamic_percentages(client, title, description):
    """Generate AI-powered percentage values for various metrics"""
    if not client:
        return None
    
    try:
        percentages_prompt = f"""Generate realistic percentage values for this property's optimization metrics:
Title: {title}
Description: {description}

Provide values in JSON format:
{{
    "search_visibility": [10-30],
    "conversion_rate": [15-35], 
    "average_rate_increase": [20-40],
    "review_probability": [30-70],
    "midweek_discount": [10-25],
    "lastminute_discount": [5-15],
    "monthly_discount": [15-30],
    "seasonal_increase": [5-20],
    "minimum_stay_revenue": [30-60],
    "holiday_premium": [30-70],
    "extended_stay_discount": [15-25],
    "early_bird_discount": [5-15]
}}

Base on property type and market positioning."""
        
        percentages_response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a pricing strategy expert for vacation rentals."},
                {"role": "user", "content": percentages_prompt}
            ]
        )
        
        import json
        percentages_data = json.loads(percentages_response.choices[0].message.content.strip())
        return percentages_data
        
    except Exception as e:
        print(f"Dynamic percentages generation error: {e}")
        return None 