from typing import Dict, Any, List

# Rarity tiers and base catch probabilities (assuming base rod)
RARITIES = {
    "common": {"weight": 100, "xp_mult": 1.0, "price_mult": 1.0},
    "uncommon": {"weight": 50, "xp_mult": 2.0, "price_mult": 3.0},
    "rare": {"weight": 15, "xp_mult": 5.0, "price_mult": 10.0},
    "epic": {"weight": 5, "xp_mult": 15.0, "price_mult": 50.0},
    "legendary": {"weight": 1, "xp_mult": 50.0, "price_mult": 500.0},
}

FISH_DB = {
    "bass": {"name": "Bass", "rarity": "common", "base_price": 5, "base_xp": 10},
    "trout": {"name": "Trout", "rarity": "common", "base_price": 6, "base_xp": 12},
    "catfish": {"name": "Catfish", "rarity": "uncommon", "base_price": 10, "base_xp": 20},
    "salmon": {"name": "Salmon", "rarity": "uncommon", "base_price": 12, "base_xp": 25},
    "swordfish": {"name": "Swordfish", "rarity": "rare", "base_price": 30, "base_xp": 50},
    "shark": {"name": "Shark", "rarity": "epic", "base_price": 100, "base_xp": 150},
    "kraken": {"name": "Kraken", "rarity": "legendary", "base_price": 1000, "base_xp": 1000},
}

# Items database
# Effects might include:
#  - "luck": multiplier on rare fish weights
#  - "xp": multiplier on xp gained
#  - "money": multiplier on fish sold
ITEMS_DB = {
    "cigarettes": {
        "name": "Pack of Cigarettes",
        "price": 20,
        "type": "consumable",
        "description": "Increases your luck catching rare fish by 50% for 5 minutes.",
        "duration": 300, # 5 minutes in seconds
        "effects": {
            "luck": 1.5
        }
    },
    "beer": {
        "name": "Cold Beer",
        "price": 15,
        "type": "consumable",
        "description": "Relaxes you, giving 20% more XP for 10 minutes.",
        "duration": 600,
        "effects": {
            "xp_mult": 1.2
        }
    },
    "coffee": {
        "name": "Coffee",
        "price": 30,
        "type": "consumable",
        "description": "Keeps you alert, reducing cast time or increasing total fish amount.",
        "duration": 300,
        "effects": {
            "catch_rate_mult": 1.5
        }
    }
}

RODS_DB = {
    "basic_rod": {
        "name": "Basic Rod",
        "price": 0, # Starting item
        "luck_mult": 1.0,
        "catch_rate_mult": 1.0,
        "next_upgrade": "fiberglass_rod"
    },
    "fiberglass_rod": {
        "name": "Fiberglass Rod",
        "price": 100,
        "luck_mult": 1.2,
        "catch_rate_mult": 1.1,
        "next_upgrade": "carbon_fiber_rod"
    },
    "carbon_fiber_rod": {
        "name": "Carbon Fiber Rod",
        "price": 500,
        "luck_mult": 1.5,
        "catch_rate_mult": 1.5,
        "next_upgrade": "golden_rod"
    },
    "golden_rod": {
        "name": "Golden Rod",
        "price": 2500,
        "luck_mult": 3.0,
        "catch_rate_mult": 2.0,
        "next_upgrade": None
    }
}
