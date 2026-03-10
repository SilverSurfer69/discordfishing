import random
from typing import Tuple, Optional, List, Dict
from .models import Player
from .data import FISH_DB, ITEMS_DB, RODS_DB, RARITIES

class GameEngine:
    def __init__(self, player: Player):
        self.player = player

    def _get_active_effects(self) -> Dict[str, float]:
        """Aggregate all effects from active buffs and current rod."""
        effects = {
            "luck": 1.0,
            "xp_mult": 1.0,
            "catch_rate_mult": 1.0
        }

        # Add Rod modifiers
        rod_data = RODS_DB.get(self.player.rod)
        if rod_data:
            effects["luck"] *= rod_data.get("luck_mult", 1.0)
            effects["catch_rate_mult"] *= rod_data.get("catch_rate_mult", 1.0)

        # Add consumable modifiers
        active_buffs = self.player.get_active_buffs()
        for buff_id in active_buffs:
            item_data = ITEMS_DB.get(buff_id)
            if item_data and "effects" in item_data:
                for effect_name, mult in item_data["effects"].items():
                    if effect_name in effects:
                        effects[effect_name] *= mult

        return effects

    def cast_line(self) -> Optional[str]:
        """
        Calculates whether a fish is caught and which one, based on active buffs and rod.
        Returns the ID of the fish caught, or None if nothing was caught.
        """
        effects = self._get_active_effects()

        # Calculate base catch chance
        # For simplicity, catch chance is say 70% modified by catch_rate_mult
        base_catch_chance = 0.7 * effects["catch_rate_mult"]

        if random.random() > base_catch_chance:
            return None # Missed!

        # Determine Rarity
        # Luck increases weight of uncommon+ rarities
        luck = effects["luck"]

        rarity_weights = {}
        for rarity, data in RARITIES.items():
            if rarity == "common":
                rarity_weights[rarity] = data["weight"]
            else:
                rarity_weights[rarity] = data["weight"] * luck

        # Roll for rarity
        total_weight = sum(rarity_weights.values())
        roll = random.uniform(0, total_weight)

        chosen_rarity = "common"
        cumulative = 0.0
        for rarity, weight in rarity_weights.items():
            cumulative += weight
            if roll <= cumulative:
                chosen_rarity = rarity
                break

        # Pick a random fish from the chosen rarity
        fish_in_rarity = [f_id for f_id, f_data in FISH_DB.items() if f_data["rarity"] == chosen_rarity]
        if not fish_in_rarity:
            # Fallback in case of empty rarity
            fish_in_rarity = list(FISH_DB.keys())

        return random.choice(fish_in_rarity)

    def process_catch(self, fish_id: str) -> Tuple[int, int]:
        """
        Process the rewards for catching a fish.
        Returns (xp_gained, money_gained).
        """
        fish_data = FISH_DB.get(fish_id)
        if not fish_data:
            return 0, 0

        rarity_data = RARITIES.get(fish_data["rarity"])
        effects = self._get_active_effects()

        xp_gained = int(fish_data["base_xp"] * rarity_data["xp_mult"] * effects["xp_mult"])

        # Don't give money immediately, add fish to inventory to be sold later.
        self.player.add_xp(xp_gained)
        self.player.add_item(fish_id, 1) # add to inventory

        return xp_gained, 0 # We return 0 money gained directly from catching.

    def sell_fish(self, fish_id: str, count: int) -> Tuple[bool, int]:
        """Sell fish from inventory."""
        if self.player.remove_item(fish_id, count):
            fish_data = FISH_DB[fish_id]
            rarity_data = RARITIES[fish_data["rarity"]]
            total_money = int(fish_data["base_price"] * rarity_data["price_mult"]) * count
            self.player.add_money(total_money)
            return True, total_money
        return False, 0

    def sell_all_fish(self) -> int:
        """Sells all fish in the player's inventory and returns the total money gained."""
        total_gained = 0
        fish_ids = list(FISH_DB.keys())

        # Check player inventory for these fish
        for fish_id in fish_ids:
            count = self.player.inventory.get(fish_id, 0)
            if count > 0:
                success, money = self.sell_fish(fish_id, count)
                if success:
                    total_gained += money

        return total_gained

    def buy_item(self, item_id: str) -> bool:
        """Buy a consumable item from the shop."""
        item_data = ITEMS_DB.get(item_id)
        if not item_data:
            return False

        price = item_data["price"]
        if self.player.remove_money(price):
            self.player.add_item(item_id, 1)
            return True
        return False

    def use_item(self, item_id: str) -> bool:
        """Use a consumable item to gain buffs."""
        item_data = ITEMS_DB.get(item_id)
        if not item_data or item_data["type"] != "consumable":
            return False

        if self.player.remove_item(item_id, 1):
            self.player.add_buff(item_id, item_data["duration"])
            return True
        return False

    def get_rod_upgrade_cost(self) -> Optional[int]:
        """Returns the cost to upgrade the rod, or None if fully upgraded."""
        current_rod_data = RODS_DB.get(self.player.rod)
        if not current_rod_data or not current_rod_data.get("next_upgrade"):
            return None

        next_rod_id = current_rod_data["next_upgrade"]
        next_rod_data = RODS_DB.get(next_rod_id)
        if not next_rod_data:
            return None

        return next_rod_data["price"]

    def upgrade_rod(self) -> Tuple[bool, str]:
        """Upgrades the player's rod if they have enough money."""
        current_rod_data = RODS_DB.get(self.player.rod)
        if not current_rod_data or not current_rod_data.get("next_upgrade"):
            return False, "Your rod is fully upgraded."

        next_rod_id = current_rod_data["next_upgrade"]
        next_rod_data = RODS_DB.get(next_rod_id)

        price = next_rod_data["price"]
        if self.player.remove_money(price):
            self.player.rod = next_rod_id
            return True, f"Successfully upgraded to {next_rod_data['name']}!"

        return False, "Not enough money to upgrade."
