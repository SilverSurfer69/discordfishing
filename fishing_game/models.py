from typing import Dict, List, Optional
import time

class Player:
    def __init__(self, name: str):
        self.name = name
        self.level = 1
        self.xp = 0
        self.money = 0

        # Current active rod id
        self.rod = "basic_rod"

        # inventory counts by item_id
        self.inventory: Dict[str, int] = {}

        # active buffs
        # buff_name -> expiration timestamp
        self.active_buffs: Dict[str, float] = {}

    def get_xp_required_for_next_level(self) -> int:
        """Rich leveling: simple exponential scaling"""
        return int(100 * (1.5 ** (self.level - 1)))

    def add_xp(self, amount: int):
        self.xp += amount
        while self.xp >= self.get_xp_required_for_next_level():
            self.xp -= self.get_xp_required_for_next_level()
            self.level += 1

    def add_money(self, amount: int):
        self.money += amount

    def remove_money(self, amount: int) -> bool:
        if self.money >= amount:
            self.money -= amount
            return True
        return False

    def add_item(self, item_id: str, count: int = 1):
        self.inventory[item_id] = self.inventory.get(item_id, 0) + count

    def remove_item(self, item_id: str, count: int = 1) -> bool:
        if self.inventory.get(item_id, 0) >= count:
            self.inventory[item_id] -= count
            if self.inventory[item_id] == 0:
                del self.inventory[item_id]
            return True
        return False

    def add_buff(self, buff_id: str, duration_seconds: int):
        current_time = time.time()
        # If buff is already active, extend it or just override with new duration if it's longer?
        # Let's say it overrides with the new expiration if it's further in the future
        new_expiration = current_time + duration_seconds

        if buff_id in self.active_buffs:
            if new_expiration > self.active_buffs[buff_id]:
                 self.active_buffs[buff_id] = new_expiration
        else:
            self.active_buffs[buff_id] = new_expiration

    def is_buff_active(self, buff_id: str) -> bool:
        if buff_id not in self.active_buffs:
            return False

        if time.time() > self.active_buffs[buff_id]:
            # Expired
            del self.active_buffs[buff_id]
            return False

        return True

    def get_active_buffs(self) -> List[str]:
        current_time = time.time()
        active = []
        expired = []
        for buff_id, exp_time in self.active_buffs.items():
            if current_time <= exp_time:
                active.append(buff_id)
            else:
                expired.append(buff_id)

        # cleanup
        for buff_id in expired:
            del self.active_buffs[buff_id]

        return active
