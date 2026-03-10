import sys
import time
from typing import Optional
from fishing_game.models import Player
from fishing_game.engine import GameEngine
from fishing_game.data import FISH_DB, ITEMS_DB, RODS_DB, RARITIES

def print_separator():
    print("-" * 50)

def print_menu():
    print_separator()
    print("Welcome to the Fishing Game!")
    print("1. Cast your line")
    print("2. View Stats & Inventory")
    print("3. Shop (Buy Items & Upgrades)")
    print("4. Use Item")
    print("5. Sell All Fish")
    print("6. Quit")
    print_separator()

def main():
    player_name = input("Enter your player name: ")
    player = Player(player_name)
    engine = GameEngine(player)

    # Give some starting money for testing
    player.add_money(50)

    while True:
        print_menu()
        choice = input("Enter your choice (1-6): ")

        if choice == '1':
            print("Casting line...")
            time.sleep(1) # Dramatic pause

            fish_id = engine.cast_line()
            if not fish_id:
                print("Darn, you missed! Try again.")
            else:
                xp, money = engine.process_catch(fish_id)
                fish_data = FISH_DB[fish_id]
                rarity = fish_data["rarity"]

                print(f"\n*** You caught a {fish_data['name']}! ***")
                print(f"Rarity: {rarity.capitalize()}")
                print(f"Gained {xp} XP and {money} coins!")

        elif choice == '2':
            print_separator()
            print(f"Stats for {player.name}:")
            print(f"Level: {player.level}")
            print(f"XP: {player.xp} / {player.get_xp_required_for_next_level()}")
            print(f"Money: {player.money} coins")
            print(f"Rod: {RODS_DB[player.rod]['name']}")

            print("\nActive Buffs:")
            active_buffs = player.get_active_buffs()
            if not active_buffs:
                print("None")
            else:
                for buff_id in active_buffs:
                    item_data = ITEMS_DB[buff_id]
                    time_left = int(player.active_buffs[buff_id] - time.time())
                    print(f"- {item_data['name']} ({time_left}s left)")

            print("\nInventory:")
            if not player.inventory:
                print("Empty")
            else:
                for item_id, count in player.inventory.items():
                    name = FISH_DB.get(item_id, {}).get("name") or ITEMS_DB.get(item_id, {}).get("name")
                    print(f"- {name}: {count}")

        elif choice == '3':
            print_separator()
            print("--- Shop ---")
            print(f"Your Money: {player.money}")

            upgrade_cost = engine.get_rod_upgrade_cost()
            if upgrade_cost is not None:
                next_rod_data = RODS_DB[RODS_DB[player.rod]["next_upgrade"]]
                print(f"0. Upgrade Rod to {next_rod_data['name']} ({upgrade_cost} coins)")

            for i, (item_id, data) in enumerate(ITEMS_DB.items(), 1):
                print(f"{i}. Buy {data['name']} ({data['price']} coins) - {data['description']}")

            print(f"{len(ITEMS_DB) + 1}. Cancel")

            shop_choice = input("Enter choice: ")

            if shop_choice == '0' and upgrade_cost is not None:
                success, msg = engine.upgrade_rod()
                print(msg)
            elif shop_choice.isdigit():
                idx = int(shop_choice)
                if 1 <= idx <= len(ITEMS_DB):
                    item_id = list(ITEMS_DB.keys())[idx - 1]
                    if engine.buy_item(item_id):
                        print(f"Successfully bought {ITEMS_DB[item_id]['name']}!")
                    else:
                        print("Not enough money!")

        elif choice == '4':
            print_separator()
            print("--- Use Item ---")

            consumables = [
                (item_id, count) for item_id, count in player.inventory.items()
                if item_id in ITEMS_DB and ITEMS_DB[item_id]["type"] == "consumable"
            ]

            if not consumables:
                print("You don't have any usable items.")
                continue

            for i, (item_id, count) in enumerate(consumables, 1):
                print(f"{i}. {ITEMS_DB[item_id]['name']} (x{count})")

            print(f"{len(consumables) + 1}. Cancel")

            use_choice = input("Enter choice: ")
            if use_choice.isdigit():
                idx = int(use_choice)
                if 1 <= idx <= len(consumables):
                    item_id = consumables[idx - 1][0]
                    if engine.use_item(item_id):
                        print(f"Used {ITEMS_DB[item_id]['name']}! Buff applied.")
                    else:
                        print("Failed to use item.")

        elif choice == '5':
            print("Selling all fish...")
            money_gained = engine.sell_all_fish()
            if money_gained > 0:
                print(f"Sold all fish for {money_gained} coins!")
            else:
                print("No fish to sell.")

        elif choice == '6':
            print("Thanks for playing!")
            break

        else:
            print("Invalid choice, please try again.")

if __name__ == "__main__":
    main()
