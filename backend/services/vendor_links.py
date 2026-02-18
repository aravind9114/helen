"""
Direct vendor link generator - more reliable than web search.
Maps categories to actual vendor URLs with real furniture.
"""
from typing import List, Dict


class VendorLinks:
    """Generate direct vendor links for furniture categories"""
    
    # Real vendor URLs for each category
    VENDOR_DIRECTORY = {
        "sofa": [
            {
                "title": "Sofas at Pepperfry - Buy 2 & 3 Seater Sofas Online",
                "link": "https://www.pepperfry.com/furniture/sofas.html",
                "snippet": "Shop from wide range of sofas online. Choose from 2-seater, 3-seater, L-shaped sofas. Prices starting from ₹15,000. Fast delivery across India.",
                "domain": "pepperfry.com",
                "approx_price": 15000,
                "vendor": "Pepperfry"
            },
            {
                "title": "Urban Ladder Sofas - Modern & Classic Designs",
                "link": "https://www.urbanladder.com/sofas",
                "snippet": "Premium sofas with express delivery. Choose fabric, leather, or velvet sofas. Starting at ₹18,999. Free assembly included.",
                "domain": "urbanladder.com",
                "approx_price": 18999,
                "vendor": "Urban Ladder"
            },
            {
                "title": "IKEA India Sofas - Scandinavian Style",
                "link": "https://www.ikea.com/in/en/cat/sofas-fu003/",
                "snippet": "Explore IKEA's range of sofas & couches. Modern designs with comfort. Prices from ₹19,990. Visit store or order online.",
                "domain": "ikea.com",
                "approx_price": 19990,
                "vendor": "IKEA"
            },
            {
                "title": "Amazon India Sofas - Best Deals & Offers",
                "link": "https://www.amazon.in/s?k=sofa+set+for+living+room",
                "snippet": "Buy sofa sets online at best prices. Free shipping available. Choose from 1000+ options. Starting ₹12,999 with EMI options.",
                "domain": "amazon.in",
                "approx_price": 12999,
                "vendor": "Amazon"
            },
            {
                "title": "Furniture Online - L-Shape & Sectional Sofas",
                "link": "https://www.furnitureonline.in/sofas",
                "snippet": "Premium L-shape sofas with modern fabrics. Customization available. Prices range ₹25,000 - ₹75,000. Pan-India delivery.",
                "domain": "furnitureonline.in",
                "approx_price": 25000,
                "vendor": "Furniture Online"
            }
        ],
        "bed": [
            {
                "title": "Beds at Pepperfry - King, Queen & Single Beds",
                "link": "https://www.pepperfry.com/furniture/beds.html",
                "snippet": "Buy beds online in India. Choose from wooden, metal, upholstered beds. Starting ₹8,999. Storage beds available.",
                "domain": "pepperfry.com",
                "approx_price": 8999,
                "vendor": "Pepperfry"
            },
            {
                "title": "Urban Ladder Beds - King & Queen Size",
                "link": "https://www.urbanladder.com/beds",
                "snippet": "Premium beds with storage options. Solid wood & engineered wood. Prices from ₹14,999. Free delivery.",
                "domain": "urbanladder.com",
                "approx_price": 14999,
                "vendor": "Urban Ladder"
            },
            {
                "title": "IKEA Beds - Comfortable Sleep Solutions",
                "link": "https://www.ikea.com/in/en/cat/beds-bm003/",
                "snippet": "Explore IKEA bed frames & mattresses. Single to king size. Starting ₹12,990. Durable and stylish designs.",
                "domain": "ikea.com",
                "approx_price": 12990,
                "vendor": "IKEA"
            },
            {
                "title": "Amazon India Beds - Best Prices Online",
                "link": "https://www.amazon.in/s?k=bed+king+size",
                "snippet": "Shop king & queen size beds. Wooden, metal, hydraulic storage beds. From ₹9,999. Fast delivery available.",
                "domain": "amazon.in",
                "approx_price": 9999,
                "vendor": "Amazon"
            },
            {
                "title": "WoodenStreet Beds - Solid Wood Collection",
                "link": "https://www.woodenstreet.com/beds",
                "snippet": "Handcrafted wooden beds in sheesham & mango wood. King size beds from ₹19,999. Customization available.",
                "domain": "woodenstreet.com",
                "approx_price": 19999,
                "vendor": "WoodenStreet"
            }
        ],
        "table": [
            {
                "title": "Dining Tables at Pepperfry - 4 & 6 Seater",
                "link": "https://www.pepperfry.com/furniture/dining-tables.html",
                "snippet": "Buy dining tables online. 4-seater, 6-seater, extendable tables. Starting ₹7,999. Glass, wood, marble options.",
                "domain": "pepperfry.com",
                "approx_price": 7999,
                "vendor": "Pepperfry"
            },
            {
                "title": "Urban Ladder Dining Tables - Modern Designs",
                "link": "https://www.urbanladder.com/dining-tables",
                "snippet": "Premium dining tables with chairs. 4 to 8 seater options. From ₹11,999. Free assembly included.",
                "domain": "urbanladder.com",
                "approx_price": 11999,
                "vendor": "Urban Ladder"
            },
            {
                "title": "IKEA Dining Tables - Scandinavian Style",
                "link": "https://www.ikea.com/in/en/cat/dining-tables-21825/",
                "snippet": "Extendable & fixed dining tables. Seats 2-8 people. Starting ₹9,990. Durable materials.",
                "domain": "ikea.com",
                "approx_price": 9990,
                "vendor": "IKEA"
            },
            {
                "title": "Amazon Dining Tables - Top Rated Collections",
                "link": "https://www.amazon.in/s?k=dining+table+6+seater",
                "snippet": "6-seater dining table sets with chairs. Wooden, glass top options. From ₹8,999 with free delivery.",
                "domain": "amazon.in",
                "approx_price": 8999,
                "vendor": "Amazon"
            },
            {
                "title": "WoodenStreet Dining Tables - Sheesham Wood",
                "link": "https://www.woodenstreet.com/dining-tables",
                "snippet": "Handcrafted wooden dining tables. 4, 6, 8 seater options. Premium sheesham wood. From ₹15,999.",
                "domain": "woodenstreet.com",
                "approx_price": 15999,
                "vendor": "WoodenStreet"
            }
        ],
        "chair": [
            {
                "title": "Chairs at Pepperfry - Office & Dining Chairs",
                "link": "https://www.pepperfry.com/furniture/chairs.html",
                "snippet": "Buy chairs online. Office chairs, dining chairs, accent chairs. Starting ₹2,999. Ergonomic designs available.",
                "domain": "pepperfry.com",
                "approx_price": 2999,
                "vendor": "Pepperfry"
            },
            {
                "title": "Urban Ladder Chairs - Ergonomic & Stylish",
                "link": "https://www.urbanladder.com/chairs",
                "snippet": "Premium office & dining chairs. Mesh back, cushioned, wooden designs. From ₹3,999. 1-year warranty.",
                "domain": "urbanladder.com",
                "approx_price": 3999,
                "vendor": "Urban Ladder"
            },
            {
                "title": "IKEA Office Chairs - Work From Home",
                "link": "https://www.ikea.com/in/en/cat/office-chairs-20652/",
                "snippet": "Ergonomic office chairs for home & office. Adjustable height, lumbar support. Starting ₹4,990.",
                "domain": "ikea.com",
                "approx_price": 4990,
                "vendor": "IKEA"
            },
            {
                "title": "Amazon Office Chairs - Best Sellers",
                "link": "https://www.amazon.in/s?k=office+chair",
                "snippet": "Top-rated office chairs with lumbar support. Mesh, leather options. From ₹2,499 with fast delivery.",
                "domain": "amazon.in",
                "approx_price": 2499,
                "vendor": "Amazon"
            },
            {
                "title": "Featherlite Chairs - Premium Office Seating",
                "link": "https://www.featherliteonline.com/office-chairs",
                "snippet": "Professional ergonomic chairs. Used in offices across India. Starting ₹5,999. 3-year warranty.",
                "domain": "featherliteonline.com",
                "approx_price": 5999,
                "vendor": "Featherlite"
            }
        ],
        "tv": [
            {
                "title": "Smart TVs at Amazon - 32 to 75 inch",
                "link": "https://www.amazon.in/s?k=smart+tv",
                "snippet": "Buy smart TVs from top brands. Samsung, LG, Sony, Mi. 43-inch 4K TVs from ₹24,999. Fast delivery.",
                "domain": "amazon.in",
                "approx_price": 24999,
                "vendor": "Amazon"
            },
            {
                "title": "Flipkart TVs - Best Deals on Smart TVs",
                "url": "https://www.flipkart.com/televisions/pr?sid=ckf",
                "snippet": "Shop LED & Smart TVs online. 32-inch HD TVs starting ₹12,999. EMI options available.",
                "domain": "flipkart.com",
                "approx_price": 12999,
                "vendor": "Flipkart"
            },
            {
                "title": "Reliance Digital TVs - Latest Models",
                "url": "https://www.reliancedigital.in/televisions/c/TV",
                "snippet": "Buy smart TVs with installation. Samsung, LG, Sony range. 55-inch 4K from ₹39,999. Exchange offers.",
                "domain": "reliancedigital.in",
                "approx_price": 39999,
                "vendor": "Reliance Digital"
            },
            {
                "title": "Croma TVs - Premium Electronics",
                "url": "https://www.croma.com/televisions/c/9",
                "snippet": "Latest 4K & 8K TVs from top brands. 43-inch onwards. Starting ₹26,999. Free installation.",
                "domain": "croma.com",
                "approx_price": 26999,
                "vendor": "Croma"
            },
            {
                "title": "Vijay Sales TVs - Best Prices Guaranteed",
                "url": "https://www.vijaysales.com/televisions",
                "snippet": "Smart TVs with best deals. All brands available. 50-inch 4K from ₹32,999. Extended warranty.",
                "domain": "vijaysales.com",
                "approx_price": 32999,
                "vendor": "Vijay Sales"
            }
        ]
    }
    
    def get_vendor_links(self, category: str) -> Dict:
        """
        Get direct vendor links for a category
        
        Returns:
            {
                "results": [...],
                "cache": "vendor_directory",
                "latency_ms": 0
            }
        """
        category = category.lower()
        
        if category in self.VENDOR_DIRECTORY:
            results = self.VENDOR_DIRECTORY[category]
            # Add source field
            for result in results:
                result["source"] = "vendor_directory"
            
            return {
                "results": results,
                "cache": "vendor_directory",
                "latency_ms": 0
            }
        else:
            return {
                "results": [],
                "cache": "vendor_directory",
                "latency_ms": 0
            }
