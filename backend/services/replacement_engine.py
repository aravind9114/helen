import json
from pathlib import Path
from typing import List, Dict
from backend.services.logging import logger

class ReplacementEngine:
    """Rule-based furniture replacement suggestions"""
    
    def __init__(self, catalog_path: str = "catalog.json"):
        self.catalog_path = Path(catalog_path)
        self.catalog = self._load_catalog()
        self.grouped_catalog = self._group_by_category()
    
    def _load_catalog(self) -> List[Dict]:
        """Load furniture catalog"""
        if not self.catalog_path.exists():
            logger.warning(f"Catalog not found at {self.catalog_path}, using empty catalog")
            return []
        
        with open(self.catalog_path, 'r') as f:
            return json.load(f)
    
    def _group_by_category(self) -> Dict[str, List[Dict]]:
        """Group catalog items by category, sorted by price"""
        grouped = {}
        
        for item in self.catalog:
            category = item.get("category", "").lower()
            if category not in grouped:
                grouped[category] = []
            grouped[category].append(item)
        
        # Sort each category by price ascending
        for category in grouped:
            grouped[category].sort(key=lambda x: x.get("price", 999999))
        
        return grouped
    
    def suggest_replacements(self, detections: List[Dict], budget: int, max_suggestions: int = 3):
        """
        Generate replacement suggestions for detected items
        
        Args:
            detections: List of detected furniture items
            budget: User's budget
            max_suggestions: Number of alternatives per item
        
        Returns:
            suggestions: List of suggestions with detected item and alternatives
            remaining_budget: Budget after suggestions
        """
        suggestions = []
        total_cost = 0
        
        for detection in detections:
            category = detection["category"]
            
            # Get cheapest alternatives from catalog
            alternatives = self.grouped_catalog.get(category, [])[:max_suggestions]
            
            if alternatives:
                # Calculate cost (use first/cheapest option)
                item_cost = alternatives[0].get("price", 0)
                total_cost += item_cost
                
                suggestions.append({
                    "detected": detection,
                    "suggested_items": alternatives
                })
        
        remaining_budget = budget - total_cost
        
        logger.info(f"Generated {len(suggestions)} replacement suggestions")
        logger.info(f"Total suggested cost: ₹{total_cost} | Remaining: ₹{remaining_budget}")
        
        return suggestions, remaining_budget
