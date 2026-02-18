"""
Web-based furniture suggestion service using DuckDuckGo search.
No API keys required, with caching and offline fallback.
"""
import json
import re
import time
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from ddgs import DDGS
from backend.services.logging import logger


class WebSuggest:
    """Search for furniture suggestions using DuckDuckGo"""
    
    def __init__(self, cache_file: str = "storage/suggest_cache.json"):
        self.cache_file = Path(cache_file)
        self.cache_ttl_hours = 24
        self._ensure_cache_dir()
    
    def _ensure_cache_dir(self):
        """Create cache directory if not exists"""
        self.cache_file.parent.mkdir(parents=True, exist_ok=True)
        if not self.cache_file.exists():
            self.cache_file.write_text("{}")
    
    def _load_cache(self) -> dict:
        """Load cache from file"""
        try:
            with open(self.cache_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.warning(f"Failed to load cache: {e}")
            return {}
    
    def _save_cache(self, cache: dict):
        """Save cache to file"""
        try:
            with open(self.cache_file, 'w') as f:
                json.dump(cache, f, indent=2)
        except Exception as e:
            logger.warning(f"Failed to save cache: {e}")
    
    def _get_cache_key(self, category: str, budget: int) -> str:
        """Generate cache key"""
        return f"{category.lower()}_{budget}"
    
    def _is_cache_valid(self, cached_time: str) -> bool:
        """Check if cache entry is still valid (within TTL)"""
        try:
            cached = datetime.fromisoformat(cached_time)
            expiry = cached + timedelta(hours=self.cache_ttl_hours)
            return datetime.now() < expiry
        except:
            return False
    
    def _extract_price(self, text: str) -> Optional[int]:
        """Extract approximate price from text snippet"""
        # Look for Indian Rupee formats: ₹25,000 or Rs. 25000 or Rs 25,000
        patterns = [
            r'₹\s*([0-9,]+)',
            r'Rs\.?\s*([0-9,]+)',
            r'INR\s*([0-9,]+)',
            r'Price:\s*([0-9,]+)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                price_str = match.group(1).replace(',', '')
                try:
                    return int(price_str)
                except ValueError:
                    continue
        return None
    
    def search_suggestions(self, category: str, budget: int = 50000, max_results: int = 5) -> Dict:
        """
        Search for furniture suggestions using DuckDuckGo
        
        Args:
            category: Furniture category (sofa, bed, table, chair, tv)
            budget: User's budget (used for cache key)
            max_results: Number of results to return
        
        Returns:
            {
                "results": [...],
                "cache": "hit" | "miss",
                "latency_ms": int
            }
        """
        start_time = time.time()
        
        # Check cache
        cache_key = self._get_cache_key(category, budget)
        cache = self._load_cache()
        
        if cache_key in cache and self._is_cache_valid(cache[cache_key].get("timestamp", "")):
            logger.info(f"✓ Cache hit for {category}")
            latency = int((time.time() - start_time) * 1000)
            return {
                "results": cache[cache_key]["results"],
                "cache": "hit",
                "latency_ms": latency
            }
        
        # Search DuckDuckGo
        logger.info(f"Searching DuckDuckGo for: {category}")
        results = []
        
        try:
            # Build multiple search query variations (prioritizing requested vendors)
            queries = [
                f"{category} amazon india",
                f"{category} flipkart furniture",
                f"{category} ikea india",
                f"{category} damro india",
                f"buy {category} online amazon flipkart"
            ]
            
            # Use DuckDuckGo search
            for query in queries:
                if len(results) >= max_results:
                    break
                
                try:
                    with DDGS() as ddgs:
                        search_results = list(ddgs.text(query, region='in-en', max_results=max_results * 2))
                    
                    if search_results:
                        logger.info(f"✓ Query '{query}' returned {len(search_results)} results")
                        # Process results
                        seen_domains = set()
                        for result in search_results:
                            if len(results) >= max_results:
                                break
                            
                            # Extract domain
                            try:
                                from urllib.parse import urlparse
                                domain = urlparse(result['href']).netloc.replace('www.', '')
                            except:
                                domain = "unknown"
                            
                            # Skip duplicates from same domain
                            if domain in seen_domains:
                                continue
                            seen_domains.add(domain)
                            
                            # Extract approximate price from snippet
                            snippet = result.get('body', '')
                            approx_price = self._extract_price(snippet)
                            
                            results.append({
                                "title": result.get('title', 'No title'),
                                "link": result['href'],
                                "snippet": snippet[:200] if snippet else "No description available",
                                "source": "duckduckgo",
                                "domain": domain,
                                "approx_price": approx_price
                            })
                        
                        # If we got enough results, break
                        if len(results) >= max_results:
                            break
                
                except Exception as e:
                    logger.warning(f"Query '{query}' failed: {e}")
                    continue
            
            # Cache results
            cache[cache_key] = {
                "results": results,
                "timestamp": datetime.now().isoformat()
            }
            self._save_cache(cache)
            
            logger.info(f"✓ Found {len(results)} suggestions for {category}")
            
        except Exception as e:
            logger.error(f"DuckDuckGo search failed: {e}")
            results = []
        
        latency = int((time.time() - start_time) * 1000)
        
        return {
            "results": results,
            "cache": "miss",
            "latency_ms": latency
        }
