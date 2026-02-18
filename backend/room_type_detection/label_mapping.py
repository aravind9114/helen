"""
Mapping from classifier labels to application room types.
Model: alessandroseni/room-type-detection (or similar)
"""

ROOM_TYPE_MAPPING = {
    "bedroom": "Bedroom",
    "livingroom": "Living Room",
    "living_room": "Living Room",
    "kitchen": "Kitchen",
    "diningroom": "Dining Room",
    "dining_room": "Dining Room",
    "bathroom": "Bathroom",
    "office": "Office",
    "children_room": "Bedroom",
    "hall": "Living Room",
    "corridor": "Hallway",
    "pantry": "Kitchen",
    "laundry": "Laundry Room",
    "balcony": "Outdoor",
    "terrace": "Outdoor",
    "garden": "Outdoor",
    "garage": "Garage",
    "entrance": "Hallway",
    "closet": "Closet",
    "staircase": "Stairs",
    "toilets": "Bathroom",
    "lobby": "Living Room"
}

def normalize_room_label(label: str) -> str:
    """Normalize local model label to canonical room type."""
    cleaned = label.lower().replace(" ", "_")
    return ROOM_TYPE_MAPPING.get(cleaned, "Unknown")
