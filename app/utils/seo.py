"""
SEO utilities for Pawfect Finds.
Provides sitemap generation, meta tags, and structured data helpers.
"""
from datetime import datetime
from typing import List, Dict, Any
from flask import url_for, request
from app.services.database import Database
from app.utils.error_handler import get_logger

logger = get_logger(__name__)


def generate_sitemap() -> str:
    """Generate XML sitemap for the website"""
    db = Database()
    
    sitemap_xml = ['<?xml version="1.0" encoding="UTF-8"?>']
    sitemap_xml.append('<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">')
    
    # Static pages
    static_pages = [
        ('public.landing', '1.0', 'daily'),
        ('public.browse_products', '0.9', 'daily'),
        ('public.about', '0.7', 'monthly'),
        ('public.contact', '0.7', 'monthly'),
        ('auth.login', '0.6', 'monthly'),
        ('auth.signup', '0.6', 'monthly'),
    ]
    
    for endpoint, priority, changefreq in static_pages:
        try:
            url = url_for(endpoint, _external=True)
            sitemap_xml.append('  <url>')
            sitemap_xml.append(f'    <loc>{url}</loc>')
            sitemap_xml.append(f'    <changefreq>{changefreq}</changefreq>')
            sitemap_xml.append(f'    <priority>{priority}</priority>')
            sitemap_xml.append('  </url>')
        except Exception as e:
            logger.warning(f"Could not generate URL for {endpoint}: {e}")
    
    # Product pages
    try:
        products = db.execute_query(
            """
            SELECT id, updated_at 
            FROM products 
            WHERE status = 'active' 
            ORDER BY updated_at DESC
            LIMIT 1000
            """,
            fetch=True
        )
        
        if products:
            for product in products:
                try:
                    url = url_for('public.product_detail', product_id=product['id'], _external=True)
                    lastmod = product['updated_at'].strftime('%Y-%m-%d') if product.get('updated_at') else ''
                    
                    sitemap_xml.append('  <url>')
                    sitemap_xml.append(f'    <loc>{url}</loc>')
                    if lastmod:
                        sitemap_xml.append(f'    <lastmod>{lastmod}</lastmod>')
                    sitemap_xml.append('    <changefreq>weekly</changefreq>')
                    sitemap_xml.append('    <priority>0.8</priority>')
                    sitemap_xml.append('  </url>')
                except Exception as e:
                    logger.warning(f"Could not generate URL for product {product['id']}: {e}")
    except Exception as e:
        logger.error(f"Error fetching products for sitemap: {e}")
    
    sitemap_xml.append('</urlset>')
    
    return '\n'.join(sitemap_xml)


def get_meta_tags(
    title: str = None,
    description: str = None,
    keywords: str = None,
    image: str = None,
    url: str = None,
    page_type: str = 'website'
) -> Dict[str, str]:
    """
    Generate meta tags for a page.
    
    Args:
        title: Page title
        description: Page description
        keywords: Comma-separated keywords
        image: OG image URL
        url: Canonical URL
        page_type: OpenGraph type (website, product, article, etc.)
    
    Returns:
        Dictionary of meta tags
    """
    # Defaults
    default_title = "Pawfect Finds - Your One-Stop Pet Shop"
    default_description = "Discover the best pet products at Pawfect Finds. Quality food, toys, accessories, and more for your beloved pets."
    default_keywords = "pet shop, pet products, dog food, cat food, pet toys, pet accessories, online pet store"
    default_image = url_for('static', filename='PF-logo.png', _external=True) if request else None
    
    # Use defaults if not provided
    title = title or default_title
    description = description or default_description
    keywords = keywords or default_keywords
    image = image or default_image
    url = url or (request.url if request else None)
    
    # Ensure title is not too long
    if len(title) > 60:
        title = title[:57] + '...'
    
    # Ensure description is not too long
    if len(description) > 160:
        description = description[:157] + '...'
    
    return {
        'title': title,
        'description': description,
        'keywords': keywords,
        'og:title': title,
        'og:description': description,
        'og:image': image,
        'og:url': url,
        'og:type': page_type,
        'og:site_name': 'Pawfect Finds',
        'twitter:card': 'summary_large_image',
        'twitter:title': title,
        'twitter:description': description,
        'twitter:image': image,
    }


def get_product_meta_tags(product: Dict[str, Any]) -> Dict[str, str]:
    """Generate meta tags for a product page"""
    title = f"{product.get('name', 'Product')} - Pawfect Finds"
    description = product.get('description', '')[:160]
    
    # Get first product image
    image = None
    if product.get('images'):
        if isinstance(product['images'], list) and len(product['images']) > 0:
            image = url_for('static', filename=product['images'][0], _external=True)
        elif isinstance(product['images'], str):
            image = url_for('static', filename=product['images'], _external=True)
    
    # Generate keywords from product data
    keywords = []
    if product.get('name'):
        keywords.append(product['name'])
    if product.get('category'):
        keywords.append(product['category'])
    if product.get('brand'):
        keywords.append(product['brand'])
    keywords.extend(['pet products', 'buy online', 'Pawfect Finds'])
    
    url = url_for('public.product_detail', product_id=product['id'], _external=True)
    
    meta_tags = get_meta_tags(
        title=title,
        description=description,
        keywords=', '.join(keywords),
        image=image,
        url=url,
        page_type='product'
    )
    
    # Add product-specific structured data
    meta_tags['product:price:amount'] = str(product.get('price', 0))
    meta_tags['product:price:currency'] = 'PHP'
    
    return meta_tags


def get_structured_data_product(product: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generate JSON-LD structured data for a product.
    Helps search engines understand product information.
    """
    image_url = None
    if product.get('images'):
        if isinstance(product['images'], list) and len(product['images']) > 0:
            image_url = url_for('static', filename=product['images'][0], _external=True)
        elif isinstance(product['images'], str):
            image_url = url_for('static', filename=product['images'], _external=True)
    
    structured_data = {
        "@context": "https://schema.org/",
        "@type": "Product",
        "name": product.get('name', ''),
        "description": product.get('description', ''),
        "image": image_url,
        "brand": {
            "@type": "Brand",
            "name": product.get('brand', 'Pawfect Finds')
        },
        "offers": {
            "@type": "Offer",
            "url": url_for('public.product_detail', product_id=product['id'], _external=True),
            "priceCurrency": "PHP",
            "price": str(product.get('price', 0)),
            "availability": "https://schema.org/InStock" if product.get('stock', 0) > 0 else "https://schema.org/OutOfStock",
            "seller": {
                "@type": "Organization",
                "name": "Pawfect Finds"
            }
        }
    }
    
    # Add rating if available
    if product.get('rating') and product.get('review_count'):
        structured_data['aggregateRating'] = {
            "@type": "AggregateRating",
            "ratingValue": str(product['rating']),
            "reviewCount": str(product['review_count'])
        }
    
    return structured_data


def get_structured_data_organization() -> Dict[str, Any]:
    """Generate JSON-LD structured data for the organization"""
    return {
        "@context": "https://schema.org",
        "@type": "PetStore",
        "name": "Pawfect Finds",
        "description": "Your one-stop shop for all pet products and supplies",
        "url": url_for('public.landing', _external=True) if request else "https://pawfectfinds.com",
        "logo": url_for('static', filename='PF-logo.png', _external=True) if request else None,
        "contactPoint": {
            "@type": "ContactPoint",
            "telephone": "+63-XXX-XXX-XXXX",
            "contactType": "Customer Service",
            "email": "support@pawfectfinds.com"
        },
        "sameAs": [
            "https://www.facebook.com/pawfectfinds",
            "https://www.instagram.com/pawfectfinds"
        ]
    }


def generate_robots_txt() -> str:
    """Generate robots.txt content"""
    sitemap_url = url_for('public.sitemap', _external=True) if request else "https://pawfectfinds.com/sitemap.xml"
    
    robots = [
        "User-agent: *",
        "Allow: /",
        "",
        "# Disallow admin and user areas",
        "Disallow: /admin/",
        "Disallow: /user/",
        "Disallow: /seller/",
        "Disallow: /rider/",
        "Disallow: /cart/",
        "Disallow: /order/",
        "",
        "# Disallow search and filter URLs",
        "Disallow: /search?*",
        "Disallow: /*?sort=*",
        "",
        f"Sitemap: {sitemap_url}",
    ]
    
    return '\n'.join(robots)
