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
                "title": "Flipkart Furniture - Sofas & Recliners",
                "link": "https://www.flipkart.com/furniture/sofas/pr?sid=wwe,c3z",
                "snippet": "Shop for Sofas online at best prices in India. 3 Seater, L Shape, Fabric & Leather Sofas. Minimum 50% Off.",
                "domain": "flipkart.com",
                "approx_price": 14999,
                "vendor": "Flipkart"
            },
            {
                "title": "Amazon.in: Sofa Sets",
                "link": "https://www.amazon.in/sofa-set/s?k=sofa+set",
                "snippet": "Explore a wide range of Sofa Sets at Amazon.in. Great designs, durable materials, and affordable prices.",
                "domain": "amazon.in",
                "approx_price": 12999,
                "vendor": "Amazon"
            },
            {
                "title": "Damro Sofas - Living Room Furniture",
                "link": "https://www.damroindia.com/living-room/sofas.html",
                "snippet": "Damro Sofas. Modern, Classic & Contemporary Designs. High quality fabric and leather sofas.",
                "domain": "damroindia.com",
                "approx_price": 22000,
                "vendor": "Damro"
            },
            {
                "title": "Pepperfry Sofas - Buy 2 & 3 Seater Sofas Online",
                "link": "https://www.pepperfry.com/furniture/sofas.html",
                "snippet": "Shop from wide range of sofas online. Choose from 2-seater, 3-seater, L-shaped sofas. Prices starting from ₹15,000.",
                "domain": "pepperfry.com",
                "approx_price": 15000,
                "vendor": "Pepperfry"
            },
            {
                "title": "IKEA India Sofas - Scandinavian Style",
                "link": "https://www.ikea.com/in/en/cat/sofas-fu003/",
                "snippet": "Explore IKEA's range of sofas & couches. Modern designs with comfort. Prices from ₹19,990.",
                "domain": "ikea.com",
                "approx_price": 19990,
                "vendor": "IKEA"
            }
        ],
        "bed": [
            {
                "title": "Flipkart Beds - King, Queen & Single",
                "link": "https://www.flipkart.com/furniture/beds/pr?sid=wwe,7p7",
                "snippet": "Buy Beds Online in India. Solid Wood, Metal, & Upholstered Beds. Free Delivery & Assembly.",
                "domain": "flipkart.com",
                "approx_price": 11999,
                "vendor": "Flipkart"
            },
            {
                "title": "Amazon.in: Beds & Bed Frames",
                "link": "https://www.amazon.in/gp/browse.html?node=1380036031",
                "snippet": "Find the perfect bed for your bedroom. Storage beds, platform beds, bunk beds at Amazon.in.",
                "domain": "amazon.in",
                "approx_price": 10500,
                "vendor": "Amazon"
            },
            {
                "title": "Damro Beds - Bedroom Furniture",
                "link": "https://www.damroindia.com/bedroom/beds.html",
                "snippet": "Damro Beds. Wooden cots, storage beds, luxury beds. Durable and stylish.",
                "domain": "damroindia.com",
                "approx_price": 18000,
                "vendor": "Damro"
            },
            {
                "title": "WoodenStreet Beds - Solid Wood Collection",
                "link": "https://www.woodenstreet.com/beds",
                "snippet": "Handcrafted wooden beds in sheesham & mango wood. King size beds from ₹19,999.",
                "domain": "woodenstreet.com",
                "approx_price": 19999,
                "vendor": "WoodenStreet"
            }
        ],
        "table": [
             {
                "title": "Flipkart Dining Tables",
                "link": "https://www.flipkart.com/furniture/dining-tables-sets/pr?sid=wwe,ur9",
                "snippet": "Dining Table Sets - Buy 4 Seater, 6 Seater & 8 Seater Dining Tables Online at Best Prices.",
                "domain": "flipkart.com",
                "approx_price": 15999,
                "vendor": "Flipkart"
            },
            {
                "title": "Amazon.in: Dining Tables",
                "link": "https://www.amazon.in/Dining-Tables/b?ie=UTF8&node=1380046031",
                "snippet": "Shop for Dining Tables at Amazon.in. Glass, Wood, Marble tops available.",
                "domain": "amazon.in",
                "approx_price": 12999,
                "vendor": "Amazon"
            },
            {
                "title": "Damro Dining Tables",
                "link": "https://www.damroindia.com/dining-room/dining-tables.html",
                "snippet": "Damro Dining Tables. Elegant designs for your dining room. 4 and 6 seater options.",
                "domain": "damroindia.com",
                "approx_price": 25000,
                "vendor": "Damro"
            }
        ],
        "chair": [
            {
                "title": "Flipkart Chairs - Office & Home",
                "link": "https://www.flipkart.com/furniture/chairs/pr?sid=wwe,y7b",
                "snippet": "Buy Chairs Online. Office Chairs, Gaming Chairs, Plastic Chairs at Lowest Prices.",
                "domain": "flipkart.com",
                "approx_price": 3500,
                "vendor": "Flipkart"
            },
            {
                "title": "Amazon.in: Chairs",
                "link": "https://www.amazon.in/Chairs/b?ie=UTF8&node=1380064031",
                "snippet": "Shop for Chairs at Amazon.in. Ergonomic office chairs, dining chairs, accent chairs.",
                "domain": "amazon.in",
                "approx_price": 2800,
                "vendor": "Amazon"
            }
        ],
        "tv": [
             {
                "title": "Flipkart Smart TVs",
                "link": "https://www.flipkart.com/televisions/pr?sid=ckf",
                "snippet": "Buy Smart TVs Online. 32 inch, 43 inch, 55 inch 4K Ultra HD TVs. Exchange Offers.",
                "domain": "flipkart.com",
                "approx_price": 15999,
                "vendor": "Flipkart"
            },
            {
                 "title": "Amazon.in: Smart Televisions",
                 "link": "https://www.amazon.in/Smart-TVs/b?ie=UTF8&node=1389396031",
                 "snippet": "Smart TVs from top brands like Samsung, LG, Sony, Xiaomi. Great deals and offers.",
                 "domain": "amazon.in",
                 "approx_price": 14999,
                 "vendor": "Amazon"
            }
        ],
        "decor": [
            {
                "title": "Flipkart Home Decor",
                "link": "https://www.flipkart.com/home-decor/pr?sid=arb",
                "snippet": "Buy Home Decor Items Online. Wall Art, Clocks, Vases, Lamps & Lighting.",
                "domain": "flipkart.com",
                "approx_price": 999,
                "vendor": "Flipkart"
            },
            {
                "title": "Amazon.in: Home Decor",
                "link": "https://www.amazon.in/Home-Decor/b?ie=UTF8&node=1380374031",
                "snippet": "Shop for Home Decor at Amazon.in. Curtains, Rugs, Plants, Paintings and more.",
                "domain": "amazon.in",
                "approx_price": 850,
                "vendor": "Amazon"
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
