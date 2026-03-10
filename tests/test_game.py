import pytest
import time
from fishing_game.models import Player
from fishing_game.engine import GameEngine
from fishing_game.data import FISH_DB, ITEMS_DB, RODS_DB

def test_player_initialization():
    player = Player("Tester")
    assert player.name == "Tester"
    assert player.level == 1
    assert player.xp == 0
    assert player.money == 0
    assert player.rod == "basic_rod"

def test_leveling_system():
    player = Player("Leveler")

    # Base level 1 to 2 requires 100 xp
    xp_needed = player.get_xp_required_for_next_level()
    assert xp_needed == 100

    player.add_xp(50)
    assert player.level == 1
    assert player.xp == 50

    player.add_xp(60)
    # Total xp = 110, needs 100 to level up
    assert player.level == 2
    assert player.xp == 10

    # Level 2 to 3 requires 100 * 1.5 = 150
    xp_needed_l2 = player.get_xp_required_for_next_level()
    assert xp_needed_l2 == 150

    player.add_xp(200)
    # Total xp = 210, needs 150 to level up
    assert player.level == 3
    assert player.xp == 60

def test_shop_and_inventory():
    player = Player("Shopper")
    engine = GameEngine(player)

    player.add_money(100)

    # Buy beer (15 coins)
    success = engine.buy_item("beer")
    assert success is True
    assert player.money == 85
    assert player.inventory.get("beer") == 1

    # Cannot afford something too expensive (e.g. bamboo_rod upgrade)
    # basic to bamboo is 500 coins, player has 85
    success, msg = engine.upgrade_rod()
    assert success is False
    assert player.rod == "basic_rod"

    # Add more money and upgrade rod
    player.add_money(415) # Total 500
    success, msg = engine.upgrade_rod()
    assert success is True
    assert player.rod == "bamboo_rod"
    assert player.money == 0

def test_buffs_and_usage():
    player = Player("Buffer")
    engine = GameEngine(player)

    player.add_money(100)
    engine.buy_item("cigarettes")

    # Use item
    success = engine.use_item("cigarettes")
    assert success is True
    assert player.inventory.get("cigarettes") is None # Removed from inventory

    assert player.is_buff_active("cigarettes") is True

    # Test effect aggregation
    effects = engine._get_active_effects()
    # Cigarettes give 1.5 luck
    assert effects["luck"] == 1.5

    # Add a rod that also gives luck to see them multiply/stack correctly
    player.add_money(500)
    engine.upgrade_rod() # 500 coins, bamboo

    effects = engine._get_active_effects()
    # Bamboo gives 1.1 luck, cigarettes 1.5
    assert effects["luck"] == 1.5 * 1.1

def test_fishing_mechanics():
    player = Player("Fisher")
    engine = GameEngine(player)

    # Force a catch by making catch rate 100% and setting random to 0
    import random
    random.seed(42) # Should give predictable results

    # Catching
    fish_id = engine.cast_line()
    if fish_id:
        xp, money = engine.process_catch(fish_id)
        assert xp > 0
        assert money == 0 # Catching gives no money directly
        assert player.inventory.get(fish_id, 0) == 1

        # Sell fish
        money_gained = engine.sell_all_fish()
        assert money_gained > 0
        assert player.money == money_gained
        assert player.inventory.get(fish_id) is None # Removed after selling
