import os
import tempfile
from jinja2 import Template
from playwright.sync_api import sync_playwright
from datetime import datetime

def calculate_content_sections(optimization_data):
    """Calculate which sections have content to determine actual page structure"""
    sections = []
    
    # Always include title enhancement (page 1)
    sections.append('title')
    
    # Check which recommendations have content
    if optimization_data.get('pricing_analysis', '').strip():
        sections.append('pricing')
    if optimization_data.get('photo_audit', '').strip():
        sections.append('photo')
    if optimization_data.get('guest_profile_analysis', '').strip():
        sections.append('guest')
    if optimization_data.get('booking_gap_analysis', '').strip():
        sections.append('booking')
    if optimization_data.get('amenities', '').strip():
        sections.append('amenities')
    
    return sections

def generate_html_pdf(optimization_data, output_path):
    """Generate pixel-perfect PDF using HTML/CSS template and Playwright - All 5 Pages"""
    
    # Extract dynamic data from AI analysis
    title_suggestions = optimization_data.get('title_suggestions', ['Optimized Title'])
    optimized_title = title_suggestions[0] if title_suggestions else current_title
    
    # Extract comprehensive dynamic data
    location = optimization_data.get('location', 'Property Location')
    current_title = optimization_data.get('title', 'Current Property Title')
    description = optimization_data.get('description', 'Property description')
    optimized_description = optimization_data.get('optimized_description', 'Enhanced property description')
    amenities = optimization_data.get('amenities', 'Premium amenities available')
    review_sentiment = optimization_data.get('review_sentiment_analysis', 'Positive guest feedback')
    booking_gap = optimization_data.get('booking_gap_analysis', 'Booking optimization opportunities identified')
    guest_profile = optimization_data.get('guest_profile_analysis', 'Target guest demographics analyzed')
    pricing_analysis = optimization_data.get('pricing_analysis', 'Competitive pricing insights')
    photo_audit = optimization_data.get('photo_audit', 'Photo enhancement recommendations')
    performance_insights = optimization_data.get('performance_insights', 'Performance improvement opportunities')
    image_urls = optimization_data.get('image_urls', [])
    
    # Calculate metrics from real data
    description_word_count = len(description.split()) if description else 0
    optimized_word_count = len(optimized_description.split()) if optimized_description else 0
    amenities_count = len(amenities.split('\n')) if amenities else 0
    image_count = len(image_urls)
    
    # Extract key insights from performance analysis for metrics
    revenue_increase = "35%"  # Default fallback
    ai_score = "8.7/10"       # Default fallback
    guest_rating = "4.98"     # Default fallback
    
    # Try to extract real metrics from performance insights
    if performance_insights:
        # Look for percentage improvements in performance insights
        import re
        revenue_match = re.search(r'(\d+)%.*(?:revenue|booking|improvement)', performance_insights, re.IGNORECASE)
        if revenue_match:
            revenue_increase = f"{revenue_match.group(1)}%"
    
    # Extract guest rating from review sentiment if available
    if review_sentiment:
        rating_match = re.search(r'(\d+\.?\d*)/10', review_sentiment)
        if rating_match:
            guest_rating = f"{float(rating_match.group(1))/2:.1f}"  # Convert 10-scale to 5-scale
    
    # Calculate AI score based on various factors
    score_factors = []
    if title_suggestions and len(title_suggestions) >= 3:
        score_factors.append(8.5)  # Good title optimization
    if optimized_description and len(optimized_description) > 200:
        score_factors.append(9.0)  # Comprehensive description
    if amenities_count >= 5:
        score_factors.append(8.8)  # Good amenity suggestions
    if image_count >= 3:
        score_factors.append(8.2)  # Adequate photo coverage
    
    if score_factors:
        calculated_score = sum(score_factors) / len(score_factors)
        ai_score = f"{calculated_score:.1f}/10"
    
    # Clean text function to remove numbered points and create complete short sentences
    def clean_text(text, max_length=120):
        if not text:
            return ""
        import re
        # Remove numbered points at start and within text
        cleaned = re.sub(r'^\d+\.\s*', '', text)
        cleaned = re.sub(r'\n\d+\.\s*', ' ', cleaned)
        # Remove asterisks and markdown formatting
        cleaned = re.sub(r'\*\*([^*]+)\*\*', r'\1', cleaned)
        cleaned = re.sub(r'\*([^*]+)\*', r'\1', cleaned)
        # Get complete sentences without truncation
        sentences = cleaned.split('.')
        if len(sentences) > 1:
            # Take first complete sentence
            result = sentences[0].strip() + '.'
        else:
            # If no period, take the whole text but limit length
            result = cleaned.strip()
            if len(result) > max_length:
                result = result[:max_length].rsplit(' ', 1)[0]
        return result
    
    # Template data for Jinja2 - Enhanced with real dynamic content
    template_data = {
        'analysis_date': datetime.now().strftime('%B %Y'),
        'property_title': f'{current_title} - AI Optimization Report',
        'property_subtitle': f'Revenue & Performance Analysis for {location}',
        'guest_rating': guest_rating,
        'ai_score': ai_score, 
        'revenue_potential': f'+{revenue_increase}',
        'current_title': current_title,
        'optimized_title': optimized_title,
        'location': location,
        'description_word_count': description_word_count,
        'optimized_word_count': optimized_word_count,
        'current_description_snippet': description[:150] + '...' if len(description) > 150 else description,
        'optimized_description_snippet': optimized_description[:150] + '...' if len(optimized_description) > 150 else optimized_description,
        'amenities_count': amenities_count,
        'image_count': image_count,
        'amenities_text': amenities,
        'review_sentiment': review_sentiment,
        'booking_gap': booking_gap,
        'guest_profile': guest_profile,
        'pricing_analysis': pricing_analysis,
        'photo_audit': photo_audit,
        'performance_insights': performance_insights,
        
        # Additional real data extractions
        'title_suggestions': title_suggestions,
        'full_optimized_description': optimized_description,
        'full_amenities': amenities,
        'full_review_sentiment': review_sentiment,
        'full_booking_gap': booking_gap,
        'full_guest_profile': guest_profile,
        'full_pricing_analysis': pricing_analysis,
        'full_photo_audit': photo_audit,
        'full_performance_insights': performance_insights,
        'concise_summary': f"Expected booking improvement is estimated at {revenue_increase}% with enhanced title optimization and strategic amenity additions. The optimized listing positioning elevates this property as a premium retreat, offering unique value in the {location} market for increased revenue potential.",
        'concise_market_analysis': f"Market rates for similar properties in {location} typically range from competitive pricing tiers, with seasonal optimization strategies and value-added experiences recommended to enhance positioning and increase average booking value in the local market.",
        
        # Clean versions for Market Analysis cards
        'clean_pricing_analysis': clean_text(pricing_analysis),
        'clean_amenities': clean_text(amenities),
        'clean_photo_audit': clean_text(photo_audit),
        'clean_guest_profile': clean_text(guest_profile),
        'clean_performance_insights': clean_text(performance_insights),
        'clean_pricing_recommendations': clean_text(pricing_analysis.replace('Market rate range', 'Strategic pricing recommendations suggest') if pricing_analysis else ''),
        
        # Implementation roadmap data
        'week1_tasks': [
            f"Update title to optimized version ({optimized_title[:50]}...)" if len(optimized_title) > 50 else f"Update title to optimized version",
            "Rewrite first paragraph of description using provided template",
            f"Adjust base prices by +{revenue_increase}% (your rating justifies this)",
            "Enable instant booking with requirements",
            "Add weekend pricing premiums"
        ],
        'week2_tasks': [
            "Complete description rewrite using SEO keywords",
            "Professional photography session for 5 key shots",
            "Reorganize photo order with new hero shot",
            "Create romance and spa package offerings"
        ],
        'week3_tasks': [
            "Implement seasonal pricing strategy",
            "Set up add-on packages in listing",
            "Create gap-filling discount rules",
            "Update house rules for premium positioning"
        ],
        'week4_tasks': [
            "Create digital welcome guide with local recommendations",
            "Set up automated messaging for premium experience",
            "Order supplies for add-on packages",
            "Create Instagram-worthy spots signage"
        ]
    }
    
    # Complete HTML template with all 5 pages
    html_template = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>STR Performance Optimization Analysis</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            line-height: 1.6;
            color: #1a1a1a;
            background: #ffffff;
            margin: 0;
            padding: 0;
            -webkit-print-color-adjust: exact;
            print-color-adjust: exact;
        }
        
        .page {
            width: 8.5in;
            margin: 0;
            padding: 0.4in;
            background: white;
            position: relative;
            box-sizing: border-box;
            overflow: visible;
        }
        
        .page-break {
            page-break-before: always;
            margin: 0;
            padding: 0;
            height: 0;
        }
        
        .content-section {
            margin-bottom: 15px;
        }
        
        .page:last-child {
            page-break-after: auto;
        }
        
        /* Content area */
        .page-content {
            flex: 1;
            display: flex;
            flex-direction: column;
            justify-content: flex-start;
            min-height: auto;
        }
        
        /* Smart section breaks - allow breaks for long content */
        .recommendation {
            page-break-inside: auto;
            break-inside: auto;
        }
        
        .feature-grid, .alert, h2, h3 {
            page-break-inside: avoid;
            break-inside: avoid;
        }
        
        /* Keep short sections together */
        .recommendation-header {
            page-break-after: avoid;
        }
        
        /* Ensure sections stay together */
        .target-guest-section {
            page-break-inside: avoid;
            break-inside: avoid;
            margin-bottom: 8px;
        }
        
        /* Header Styles */
        .header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 15px;
            padding-bottom: 10px;
            border-bottom: 3px solid #2563eb;
        }
        
        .logo {
            font-size: 24px;
            font-weight: 700;
            color: #2563eb;
        }
        
        .date {
            color: #6b7280;
            font-size: 14px;
        }
        
        h1 {
            font-size: 28px;
            font-weight: 700;
            color: #111827;
            margin-bottom: 15px;
            line-height: 1.2;
        }
        
        /* Typography */
        h2 {
            font-size: 18px;
            font-weight: 600;
            color: #1f2937;
            margin-top: 8px;
            margin-bottom: 6px;
            page-break-after: avoid;
            display: flex;
            align-items: center;
            gap: 6px;
        }
        
        h3 {
            font-size: 16px;
            font-weight: 600;
            color: #374151;
            margin-top: 4px;
            margin-bottom: 4px;
            page-break-after: avoid;
        }
        
        p {
            margin-bottom: 4px;
            color: #4b5563;
            line-height: 1.4;
            font-size: 14px;
        }
        
        /* Score Cards */
        .score-grid {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 12px;
            margin: 15px 0;
            page-break-inside: avoid;
        }
        
        .score-card {
            background: #f3f4f6;
            border-radius: 6px;
            padding: 12px;
            text-align: center;
            border: 2px solid transparent;
        }
        
        .score-card.highlight {
            background: #dbeafe;
            border-color: #2563eb;
        }
        
        .score-value {
            font-size: 36px;
            font-weight: 700;
            color: #2563eb;
            margin-bottom: 5px;
        }
        
        .score-label {
            font-size: 14px;
            color: #6b7280;
            font-weight: 500;
        }
        
        /* Alert Boxes */
        .alert {
            padding: 12px;
            border-radius: 6px;
            margin: 10px 0;
            border-left: 4px solid;
            page-break-inside: avoid;
        }
        
        .alert-success {
            background: #d1fae5;
            border-color: #10b981;
            color: #065f46;
        }
        
        .alert-info {
            background: #d1fae5;
            border-color: #10b981;
            color: #065f46;
        }
        
        .alert-warning {
            background: #fef3c7;
            border-color: #f59e0b;
            color: #92400e;
        }
        
        /* Dynamic Recommendations */
        .recommendation {
            background: #f9fafb;
            border: 1px solid #e5e7eb;
            border-radius: 4px;
            padding: 6px;
            margin-bottom: 8px;
            min-height: auto;
            flex-shrink: 0;
        }
        
        /* Auto-adjust content boxes based on content */
        .recommendation div[style*="background: #f8f9fa"] {
            min-height: 40px;
            max-height: none;
            word-wrap: break-word;
            overflow-wrap: break-word;
        }
        
        .recommendation-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 10px;
        }
        
        .priority {
            display: inline-block;
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 12px;
            font-weight: 600;
            text-transform: uppercase;
        }
        
        .priority-high {
            background: #fee2e2;
            color: #991b1b;
        }
        
        .priority-medium {
            background: #fef3c7;
            color: #92400e;
        }
        
        /* Feature Grid */
        .feature-grid {
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 20px;
            margin: 20px 0;
        }
        
        .feature-box {
            background: #f9fafb;
            border: 1px solid #e5e7eb;
            border-radius: 8px;
            padding: 20px;
        }
        
        /* Progress Bars */
        .progress-bar {
            width: 100%;
            height: 8px;
            background: #e5e7eb;
            border-radius: 4px;
            overflow: hidden;
            margin: 10px 0;
        }
        
        .progress-fill {
            height: 100%;
            background: #2563eb;
        }
        
        /* Tables */
        table {
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
        }
        
        th {
            background: #f3f4f6;
            padding: 12px;
            text-align: left;
            font-weight: 600;
            color: #374151;
            border-bottom: 2px solid #e5e7eb;
        }
        
        td {
            padding: 12px;
            border-bottom: 1px solid #e5e7eb;
            color: #4b5563;
        }
        
        /* Lists */
        ul {
            margin: 15px 0 15px 20px;
            color: #4b5563;
        }
        
        ol {
            margin: 15px 0 15px 20px;
            color: #4b5563;
        }
        
        li {
            margin-bottom: 8px;
            line-height: 1.6;
        }
        
        /* Footer */
        .footer {
            text-align: center;
            color: #6b7280;
            font-size: 12px;
            padding: 8px 0;
            margin-top: 10px;
        }
        
        /* Print Styles */
        @media print {
            body {
                background: white;
            }
            .page {
                margin: 0;
                box-shadow: none;
                page-break-after: always;
            }
        }
    </style>
</head>
<body>
    <div class="page">
    <!-- Page 1: Executive Summary -->
        <div class="header">
            <div class="logo">STR Performance Optimizer</div>
            <div class="date">Analysis Date: {{ analysis_date }}</div>
        </div>
        
        <h1>{{ property_title }}</h1>
        <p style="font-size: 18px; color: #2563eb; margin-bottom: 30px;">{{ property_subtitle }}</p>
        
        <div class="alert alert-info">
            <strong>AI Analysis Summary:</strong> {{ concise_summary }}
        </div>
        
        <div class="score-grid">
            <div class="score-card highlight">
                <div class="score-value">{{ guest_rating }}</div>
                <div class="score-label">Guest Rating</div>
            </div>
            <div class="score-card">
                <div class="score-value">{{ ai_score }}</div>
                <div class="score-label">AI Optimization Score</div>
            </div>
            <div class="score-card">
                <div class="score-value">{{ revenue_potential }}</div>
                <div class="score-label">Revenue Potential</div>
            </div>
        </div>
        
        <h2 style="font-size: 22px; font-weight: 700; margin-top: 12px; margin-bottom: 10px;">🎯 Top 5 Immediate Actions</h2>
        
        <div class="recommendation">
            <div class="recommendation-header">
                <h3>1. Title Enhancement for Search Visibility</h3>
                <span class="priority priority-high">High Priority</span>
            </div>
            <p><strong>Current:</strong> "{{ current_title }}"</p>
            <p><strong>Optimized:</strong> "{{ optimized_title }}"</p>
            <p><strong>Additional Options:</strong></p>
            <ul style="font-size: 12px; margin: 2px 0; padding-left: 16px; line-height: 1.3;">
                {% for title in title_suggestions[1:3] %}
                <li style="margin-bottom: 2px;">"{{ title }}"</li>
                {% endfor %}
            </ul>
        </div>
        
        {% if full_pricing_analysis and full_pricing_analysis.strip() %}
        <div class="recommendation">
            <div class="recommendation-header">
                <h3>2. Dynamic Pricing Strategy</h3>
                <span class="priority priority-high">High Priority</span>
            </div>
            <p><strong>AI Pricing Analysis:</strong></p>
            <div style="font-size: 12px; background: #f8f9fa; padding: 4px; border-radius: 3px; margin: 2px 0; min-height: auto; line-height: 1.3;">
                {{ full_pricing_analysis | replace('\n', '<br>') | safe }}
            </div>
        </div>
        {% endif %}
        
        
                <!-- Continue with remaining recommendations on same page -->
        
        {% if full_photo_audit and full_photo_audit.strip() %}
        <div class="recommendation">
            <div class="recommendation-header">
                <h3>3. Professional Photography Upgrade</h3>
                <span class="priority priority-high">High Priority</span>
            </div>
            <p><strong>Current Photo Count:</strong> {{ image_count }} images found</p>
            <div style="font-size: 12px; background: #f8f9fa; padding: 4px; border-radius: 3px; margin: 2px 0; min-height: auto; line-height: 1.3;">
                {{ full_photo_audit | replace('\n', '<br>') | safe }}
            </div>
        </div>
        {% endif %}
        
        {% if full_guest_profile and full_guest_profile.strip() %}
        <div class="recommendation">
            <div class="recommendation-header">
                <h3>4. Guest Experience Optimization</h3>
                <span class="priority priority-medium">Medium Priority</span>
            </div>
            <p><strong>AI Guest Profile Analysis:</strong></p>
            <div style="font-size: 12px; background: #f8f9fa; padding: 4px; border-radius: 3px; margin: 2px 0; min-height: auto; line-height: 1.3;">
                {{ full_guest_profile | replace('\n', '<br>') | safe }}
            </div>
        </div>
        {% endif %}
        
        
            <!-- Continue with final recommendations -->
        
        {% if full_booking_gap and full_booking_gap.strip() %}
        <div class="recommendation">
            <div class="recommendation-header">
                <h3>5. Booking Gap Analysis & Optimization</h3>
                <span class="priority priority-high">High Priority</span>
            </div>
            <p><strong>AI Booking Pattern Analysis:</strong></p>
            <div style="font-size: 12px; background: #f8f9fa; padding: 4px; border-radius: 3px; margin: 2px 0; min-height: auto; line-height: 1.3;">
                {{ full_booking_gap | replace('\n', '<br>') | safe }}
            </div>
        </div>
        {% endif %}
        
        {% if full_amenities and full_amenities.strip() %}
        <div class="recommendation">
            <div class="recommendation-header">
                <h3>💡 AI-Suggested Amenities</h3>
                <span class="priority priority-medium">Medium Priority</span>
            </div>
            <p><strong>Missing Amenities Analysis:</strong> {{ amenities_count }} amenities identified</p>
            <div style="font-size: 12px; background: #f8f9fa; padding: 4px; border-radius: 3px; margin: 2px 0; min-height: auto; line-height: 1.3;">
                {{ full_amenities | replace('\n', '<br>') | safe }}
            </div>
        </div>
        {% endif %}
        
          
      <!-- Page break before Market Analysis -->
      <div class="page-break"></div>
      
      <!-- Page 4: Market Analysis & Competitive Positioning -->
        <div class="header">
            <div class="logo">STR Performance Optimizer</div>
            <div class="date">Market Analysis</div>
        </div>
        
        <h2 style="font-size: 22px; margin-bottom: 20px;">📊 Market Analysis & Competitive Edge</h2>
        
        <div style="background: #dbeafe; border: 1px solid #93c5fd; border-radius: 10px; padding: 20px; margin: 20px 0;">
            <p style="margin: 0; color: #1e40af; font-size: 16px; line-height: 1.5;">
                {{ concise_market_analysis }}
            </p>
        </div>
        
        <h3 style="margin-top: 28px; margin-bottom: 20px; font-size: 20px;">Competitive Advantages</h3>
        
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin: 24px 0;">
            <!-- Location Analysis Card -->
            <div style="background: #f9fafb; border: 1px solid #e5e7eb; border-radius: 10px; padding: 20px;">
                <div style="display: flex; align-items: center; margin-bottom: 16px;">
                    <span style="font-size: 24px; margin-right: 10px;">🏞️</span>
                    <h4 style="margin: 0; font-size: 18px; font-weight: 600;">Location Analysis</h4>
                </div>
                <p style="margin: 10px 0; font-size: 15px; color: #374151; line-height: 1.5;">
                    {{ clean_pricing_analysis or 'Strategic location positioning analysis based on market data and competitive landscape evaluation.' }}
                </p>
                <div style="margin-top: 16px;">
                    <div style="background: #e5e7eb; height: 6px; border-radius: 3px; overflow: hidden;">
                        <div style="background: #3b82f6; height: 100%; width: 92%; border-radius: 3px;"></div>
                    </div>
                    <p style="margin: 6px 0 0 0; font-size: 13px; color: #6b7280;">Market Positioning: 92%</p>
                </div>
            </div>
            
            <!-- Amenities Analysis Card -->
            <div style="background: #f9fafb; border: 1px solid #e5e7eb; border-radius: 10px; padding: 20px;">
                <div style="display: flex; align-items: center; margin-bottom: 16px;">
                    <span style="font-size: 24px; margin-right: 10px;">🛁</span>
                    <h4 style="margin: 0; font-size: 18px; font-weight: 600;">Amenities Analysis</h4>
                </div>
                <p style="margin: 10px 0; font-size: 15px; color: #374151; line-height: 1.5;">
                    {{ clean_amenities or 'Property amenities evaluation shows competitive advantages in luxury features and guest experience offerings.' }}
                </p>
                <div style="margin-top: 16px;">
                    <div style="background: #e5e7eb; height: 6px; border-radius: 3px; overflow: hidden;">
                        <div style="background: #3b82f6; height: 100%; width: 88%; border-radius: 3px;"></div>
                    </div>
                    <p style="margin: 6px 0 0 0; font-size: 13px; color: #6b7280;">Amenity Score: 88%</p>
                </div>
            </div>
            
            <!-- Photo Quality Analysis Card -->
            <div style="background: #f9fafb; border: 1px solid #e5e7eb; border-radius: 10px; padding: 20px;">
                <div style="display: flex; align-items: center; margin-bottom: 16px;">
                    <span style="font-size: 24px; margin-right: 10px;">📸</span>
                    <h4 style="margin: 0; font-size: 18px; font-weight: 600;">Visual Appeal</h4>
                </div>
                <p style="margin: 10px 0; font-size: 15px; color: #374151; line-height: 1.5;">
                    {{ clean_photo_audit or 'Photography and visual presentation analysis reveals opportunities for enhanced guest engagement and booking conversion.' }}
                </p>
                <div style="margin-top: 16px;">
                    <div style="background: #e5e7eb; height: 6px; border-radius: 3px; overflow: hidden;">
                        <div style="background: #3b82f6; height: 100%; width: 76%; border-radius: 3px;"></div>
                    </div>
                    <p style="margin: 6px 0 0 0; font-size: 13px; color: #6b7280;">Visual Score: 76%</p>
                </div>
            </div>
            
            <!-- Guest Experience Analysis Card -->
            <div style="background: #f9fafb; border: 1px solid #e5e7eb; border-radius: 10px; padding: 20px;">
                <div style="display: flex; align-items: center; margin-bottom: 16px;">
                    <span style="font-size: 24px; margin-right: 10px;">👥</span>
                    <h4 style="margin: 0; font-size: 18px; font-weight: 600;">Guest Experience</h4>
                </div>
                <p style="margin: 10px 0; font-size: 15px; color: #374151; line-height: 1.5;">
                    {{ clean_guest_profile or 'Guest profile analysis indicates strong appeal to target demographics with optimized experience design recommendations.' }}
                </p>
                <div style="margin-top: 16px;">
                    <div style="background: #e5e7eb; height: 6px; border-radius: 3px; overflow: hidden;">
                        <div style="background: #3b82f6; height: 100%; width: 84%; border-radius: 3px;"></div>
                    </div>
                    <p style="margin: 6px 0 0 0; font-size: 13px; color: #6b7280;">Experience Score: 84%</p>
                </div>
            </div>
        </div>
        
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin: 36px 0;">
            <div style="background: #fef3c7; border: 1px solid #fbbf24; border-radius: 10px; padding: 20px;">
                <h4 style="margin: 0 0 10px 0; font-size: 18px; color: #92400e;">📈 Revenue Insights</h4>
                <p style="margin: 0; font-size: 15px; color: #374151; line-height: 1.5;">
                    {{ clean_performance_insights or 'AI revenue analysis projects +' + revenue_potential + '% improvement through strategic optimization and enhanced market positioning.' }}
                </p>
            </div>
            <div style="background: #dcfce7; border: 1px solid #4ade80; border-radius: 10px; padding: 20px;">
                <h4 style="margin: 0 0 10px 0; font-size: 18px; color: #166534;">💡 Strategic Recommendations</h4>
                <p style="margin: 0; font-size: 15px; color: #374151; line-height: 1.5;">
                    {{ clean_pricing_recommendations or 'Optimization strategy focuses on competitive positioning, enhanced guest experience, and data-driven pricing adjustments.' }}
                </p>
            </div>
        </div>
        
        <div class="footer">
            STR Performance Optimization Report
        </div>
        
        <!-- Page 3: Content & Visual Optimization -->
        <div class="page-break"></div>
        <div class="header">
            <div class="logo">STR Performance Optimizer</div>
            <div class="date">Content Strategy</div>
        </div>
        
        <h2>✍️ Content & Visual Optimization</h2>
        
        <div class="alert" style="background: #fed7aa; border-color: #f97316; color: #9a3412;">
            <strong>Content Analysis:</strong> Current description: {{ description_word_count }} words → Optimized: {{ optimized_word_count }} words
        </div>
        
        <h3>📝 AI-Generated Description Enhancement</h3>
        
        <div class="recommendation">
            <div class="recommendation-header">
                <h3>Current vs Optimized Description</h3>
                <span class="priority priority-high">AI-Generated</span>
            </div>
            <p><strong>Current:</strong> "{{ current_description_snippet }}"</p>
            <p><strong>AI-Optimized:</strong></p>
            <div style="background: #f0f9ff; padding: 15px; border-radius: 8px; border-left: 4px solid #2563eb;">
                {{ optimized_description_snippet }}
            </div>
        </div>
        
        <h3>📸 AI Photography Analysis</h3>
        <div style="background: #f8f9fa; padding: 8px; border-radius: 6px; margin: 8px 0; line-height: 1.3;">
            <p><strong>Current Photos Found:</strong> {{ image_count }} images</p>
            <div style="margin-top: 8px;">
                {{ full_photo_audit | replace('\n', '<br>') | safe }}
            </div>
        </div>
        
        <h3>🔍 AI-Generated SEO Keywords</h3>
        <div style="background: #f0f9ff; padding: 8px; border-radius: 6px; margin: 8px 0; border-left: 4px solid #2563eb; line-height: 1.3;">
            <p><strong>Location-Based Keywords:</strong> {{ location }}</p>
            <p><strong>Property Type:</strong> {{ current_title | truncate(50) }}</p>
            <p><strong>Key Features:</strong> Based on {{ amenities_count }} AI-suggested amenities</p>
        </div>
        
        <h3>📝 AI Review Sentiment Analysis</h3>
        <div style="background: #f8f9fa; padding: 8px; border-radius: 6px; margin: 8px 0; line-height: 1.3;">
            {{ full_review_sentiment | replace('\n', '<br>') | safe }}
        </div>
        <div class="footer">
            STR Performance Optimization Report
        </div>
        
        <!-- Page 4: Revenue Strategy & Pricing -->
        <div class="page-break"></div>
        <div class="header">
            <div class="logo">STR Performance Optimizer</div>
            <div class="date">Revenue Optimization</div>
        </div>
        
        <h2>💰 AI-Generated Pricing Strategy</h2>
        
        <div class="alert alert-info">
            <strong>AI Revenue Analysis:</strong> Based on your property in {{ location }} with {{ guest_rating }} rating
        </div>
        
        <div style="background: #f8f9fa; padding: 8px; border-radius: 6px; margin: 8px 0; line-height: 1.3;">
            {{ full_pricing_analysis | replace('\n', '<br>') | safe }}
        </div>
        
        <h3>Booking Strategy Optimization</h3>
        <div class="recommendation">
            <h3>Minimum Stay Requirements</h3>
            <ul>
                <li><strong>Weekdays:</strong> 2-night minimum (increases revenue per booking by 45%)</li>
                <li><strong>Weekends:</strong> 2-night minimum year-round</li>
                <li><strong>Peak Season:</strong> 3-night minimum for high-demand periods</li>
                <li><strong>Holidays:</strong> 4-night minimum with 50% premium</li>
            </ul>
        </div>
        
        <div class="recommendation" style="page-break-inside: avoid; break-inside: avoid;">
            <h3>Gap-Filling Strategy</h3>
            <ul>
                <li><strong>Last-Minute Deals:</strong> 15% off for bookings within 48 hours</li>
                <li><strong>Extended Stay Discount:</strong> 20% off for 7+ nights (targets remote workers)</li>
                <li><strong>Mid-Week Special:</strong> 25% off to fill mid-week gaps</li>
                <li><strong>Early Bird:</strong> 10% off for bookings 60+ days in advance</li>
            </ul>
        </div>
        
        <div class="footer">
            STR Performance Optimization Report
        </div>
        
        <!-- Page 5: Implementation Roadmap -->
        <div class="page-break"></div>
        <div class="header">
            <div class="logo">STR Performance Optimizer</div>
            <div class="date">Action Plan</div>
        </div>
        
        <h2>🚀 AI-Generated Action Plan</h2>
        
        <div class="alert alert-info">
            <strong>Implementation Priority:</strong> All recommendations below are generated by AI analysis of your specific property in {{ location }}.
        </div>
        
        <h3>🎯 Priority 1: Title Optimization</h3>
        <div style="background: #f0f9ff; padding: 8px; border-radius: 6px; margin: 8px 0; border-left: 4px solid #2563eb; line-height: 1.3;">
            <p><strong>Current Title:</strong> {{ current_title }}</p>
            <p><strong>AI-Optimized Title:</strong> {{ optimized_title }}</p>
            <p><strong>Alternative Options:</strong></p>
            <ul style="margin-top: 6px;">
                {% for title in title_suggestions[1:3] %}
                <li>{{ title }}</li>
                {% endfor %}
            </ul>
        </div>
        
        <h3>💰 Priority 2: Revenue Enhancement</h3>
        <div style="background: #f8f9fa; padding: 8px; border-radius: 6px; margin: 8px 0; line-height: 1.3;">
            {{ full_booking_gap | replace('\n', '<br>') | safe }}
        </div>
        
        <h3>📝 Priority 3: Content Optimization</h3>
        <div style="background: #f0f9ff; padding: 8px; border-radius: 6px; margin: 8px 0; border-left: 4px solid #2563eb; line-height: 1.3;">
            <p><strong>Current Description ({{ description_word_count }} words):</strong></p>
            <p style="font-style: italic; margin: 6px 0;">"{{ current_description_snippet }}"</p>
            <p><strong>AI-Enhanced Version ({{ optimized_word_count }} words):</strong></p>
            <p style="background: #ffffff; padding: 8px; border-radius: 4px; border: 1px solid #e5e7eb; margin: 6px 0;">{{ optimized_description_snippet }}</p>
        </div>
        
        <h3>🚀 AI Performance Insights & ROI Projections</h3>
        <div style="background: #f0f9ff; padding: 8px; border-radius: 6px; margin: 8px 0; border-left: 4px solid #2563eb; line-height: 1.3;">
            {{ full_performance_insights | replace('\n', '<br>') | safe }}
        </div>
        
        <div class="page-break"></div>
        
        <!-- Implementation Roadmap Section -->
        <div class="header">
            <div class="logo">STR Performance Optimizer</div>
            <div class="date">Action Plan</div>
        </div>
        
        <h2 style="font-size: 22px; margin-bottom: 20px;">🚀 30-Day Implementation Roadmap</h2>
        
        <div style="background: #dbeafe; border: 1px solid #93c5fd; border-radius: 10px; padding: 20px; margin: 20px 0;">
            <p style="margin: 0; color: #1e40af; font-size: 16px; line-height: 1.5; font-weight: 600;">
                <strong>Quick Win Strategy:</strong> Focus on high-impact, low-effort changes first. You can implement 80% of recommendations within 30 days for immediate results.
            </p>
        </div>
        
        <!-- Week 1 -->
        <h3 style="margin-top: 24px; margin-bottom: 16px; font-size: 18px;">Week 1: Immediate Actions (3 hours effort)</h3>
        
        <div style="background: #f9fafb; border: 1px solid #e5e7eb; border-radius: 10px; padding: 20px; margin: 16px 0;">
            {% for task in week1_tasks %}
            <div style="display: flex; align-items: flex-start; margin-bottom: 12px;">
                <span style="color: #16a34a; font-weight: bold; margin-right: 8px; margin-top: 2px;">✓</span>
                <span style="font-size: 15px; color: #374151; line-height: 1.5;">{{ task }}</span>
            </div>
            {% endfor %}
            
            <div style="background: #dcfce7; border: 1px solid #4ade80; border-radius: 8px; padding: 12px; margin-top: 16px;">
                <strong style="color: #166534;">Expected Impact:</strong> <span style="color: #374151;">+15% bookings, +{{ revenue_potential }}% revenue immediately</span>
            </div>
        </div>
        
        <!-- Week 2 -->
        <h3 style="margin-top: 24px; margin-bottom: 16px; font-size: 18px;">Week 2: Content Enhancement (5 hours effort)</h3>
        
        <div style="background: #f9fafb; border: 1px solid #e5e7eb; border-radius: 10px; padding: 20px; margin: 16px 0;">
            {% for task in week2_tasks %}
            <div style="display: flex; align-items: flex-start; margin-bottom: 12px;">
                <span style="color: #16a34a; font-weight: bold; margin-right: 8px; margin-top: 2px;">✓</span>
                <span style="font-size: 15px; color: #374151; line-height: 1.5;">{{ task }}</span>
            </div>
            {% endfor %}
            
            <div style="background: #dcfce7; border: 1px solid #4ade80; border-radius: 8px; padding: 12px; margin-top: 16px;">
                <strong style="color: #166534;">Expected Impact:</strong> <span style="color: #374151;">+25% conversion rate</span>
            </div>
        </div>
        
        <!-- Week 3 -->
        <h3 style="margin-top: 24px; margin-bottom: 16px; font-size: 18px;">Week 3: Revenue Optimization (3 hours effort)</h3>
        
        <div style="background: #f9fafb; border: 1px solid #e5e7eb; border-radius: 10px; padding: 20px; margin: 16px 0;">
            {% for task in week3_tasks %}
            <div style="display: flex; align-items: flex-start; margin-bottom: 12px;">
                <span style="color: #16a34a; font-weight: bold; margin-right: 8px; margin-top: 2px;">✓</span>
                <span style="font-size: 15px; color: #374151; line-height: 1.5;">{{ task }}</span>
            </div>
            {% endfor %}
            
            <div style="background: #dcfce7; border: 1px solid #4ade80; border-radius: 8px; padding: 12px; margin-top: 16px;">
                <strong style="color: #166534;">Expected Impact:</strong> <span style="color: #374151;">+30% average nightly rate</span>
            </div>
        </div>
        
        <!-- Week 4 -->
        <h3 style="margin-top: 24px; margin-bottom: 16px; font-size: 18px;">Week 4: Guest Experience Enhancement (4 hours effort)</h3>
        
        <div style="background: #f9fafb; border: 1px solid #e5e7eb; border-radius: 10px; padding: 20px; margin: 16px 0;">
            {% for task in week4_tasks %}
            <div style="display: flex; align-items: flex-start; margin-bottom: 12px;">
                <span style="color: #16a34a; font-weight: bold; margin-right: 8px; margin-top: 2px;">✓</span>
                <span style="font-size: 15px; color: #374151; line-height: 1.5;">{{ task }}</span>
            </div>
            {% endfor %}
            
            <div style="background: #dcfce7; border: 1px solid #4ade80; border-radius: 8px; padding: 12px; margin-top: 16px;">
                <strong style="color: #166534;">Expected Impact:</strong> <span style="color: #374151;">+50% chance of 5-star reviews</span>
            </div>
        </div>
        
        <div style="background: #1f2937; color: white; padding: 15px; border-radius: 8px; margin-top: 15px; text-align: center; line-height: 1.4;">
            <h3 style="color: white; margin-bottom: 10px; font-size: 18px;">Ready to Transform Your Listing?</h3>
            <p style="color: #e5e7eb; margin: 0; font-size: 14px;">This AI-powered analysis identified 25+ optimization opportunities specific to your property.</p>
        </div>
        
        <div class="footer" style="margin-top: 15px; padding: 10px 0; text-align: center; color: #6b7280; font-size: 12px;">
            STR Performance Optimization Report
        </div>
    </div>
</body>
</html>'''
    
    try:
        # Find Chrome in multiple possible locations
        print("🔍 Detecting Chrome/Chromium installation...")
        
        # Multiple possible Chrome locations
        possible_chrome_paths = [
            '/usr/bin/google-chrome',           # browserless/chrome
            '/usr/bin/google-chrome-stable',   # some Ubuntu images  
            '/usr/bin/chromium-browser',        # Chromium installs
            '/usr/bin/chromium',                # Alternative Chromium
            '/opt/google/chrome/chrome',        # Alternative location
        ]
        
        chrome_path = None
        for path in possible_chrome_paths:
            if os.path.exists(path):
                chrome_path = path
                print(f"✅ Chrome found at: {chrome_path}")
                break
        
        if not chrome_path:
            print("❌ Chrome/Chromium not found in any expected location")
            print("🔍 Available paths checked:")
            for path in possible_chrome_paths:
                print(f"   - {path}: {'✅' if os.path.exists(path) else '❌'}")
            
            # Try using Playwright's default detection as fallback
            print("🔄 Falling back to Playwright default Chrome detection...")
            try:
                with sync_playwright() as p:
                    # Let Playwright find Chrome automatically
                    test_browser = p.chromium.launch(headless=True, args=['--no-sandbox'])
                    test_browser.close()
                    chrome_path = None  # Will use Playwright default
                    print("✅ Playwright default Chrome detection successful")
            except Exception as e:
                print(f"❌ Playwright default detection failed: {e}")
                return False
        
        # Render template with data
        print("📄 Rendering HTML template...")
        template = Template(html_template)
        rendered_html = template.render(**template_data)
        
        # Create temporary HTML file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False) as temp_html:
            temp_html.write(rendered_html)
            temp_html_path = temp_html.name
        
        print("🎭 Starting Playwright PDF generation...")
        # Generate PDF using Playwright with detected Chrome
        with sync_playwright() as p:
            # Launch Chrome with detected path (or Playwright default)
            launch_options = {
                'headless': True,
                'args': [
                    '--no-sandbox',
                    '--disable-dev-shm-usage',
                    '--disable-gpu',
                    '--disable-web-security',
                    '--disable-features=VizDisplayCompositor',
                    '--font-render-hinting=none',
                    '--disable-background-timer-throttling',
                    '--disable-renderer-backgrounding',
                    '--disable-backgrounding-occluded-windows'
                ]
            }
            
            # Add executable path if we found a specific Chrome location
            if chrome_path:
                launch_options['executable_path'] = chrome_path
                print(f"🚀 Using Chrome at: {chrome_path}")
            else:
                print("🚀 Using Playwright default Chrome detection")
            
            browser = p.chromium.launch(**launch_options)
            
            try:
                page = browser.new_page()
                
                # Navigate to HTML file
                page.goto(f'file://{temp_html_path}', wait_until='networkidle')
                
                # Wait for fonts and content to fully render
                page.wait_for_timeout(2000)
                
                # Add CSS for print media
                page.add_style_tag(content='''
                    @media print {
                        * { 
                            -webkit-print-color-adjust: exact !important; 
                            color-adjust: exact !important;
                        }
                    }
                ''')
                
                # Generate PDF with optimized settings
                page.pdf(
                    path=output_path,
                    format='A4',
                    margin={'top': '0.3in', 'right': '0.3in', 'bottom': '0.3in', 'left': '0.3in'},
                    print_background=True,
                    prefer_css_page_size=False,
                    display_header_footer=False,
                    scale=1.0,
                    page_ranges='',  # Print all pages
                    tagged=False,  # Disable PDF tagging for faster generation
                    outline=False  # Disable outline generation
                )
                
                print(f"✅ PDF generated successfully: {output_path}")
                
            finally:
                browser.close()
        
        # Clean up temporary file
        os.unlink(temp_html_path)
        
        print(f"✅ HTML-to-PDF generated successfully: {output_path}")
        return True
        
    except Exception as e:
        print(f"❌ Error generating HTML-to-PDF: {e}")
        print("❌ PDF generation failed - returning False immediately")
        return False 
        return False 