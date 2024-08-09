import pandas as pd
from datetime import datetime, timedelta
import numpy as np
from enum import Enum
import json
import time

class Player:
    def __init__(self, player_id, name, level=1, gear_score=0):
        self.player_id = player_id
        self.name = name
        self.level = level
        self.gear_score = gear_score
        self.achievements = []
        self.login_history = []
        self.playtime = 0
        self.friends_list = []
        self.payment_history = []
        self.guild = None
        self.experience = 0
        self.inventory = []
        self.last_login = None
        self.total_spent = 0

    def add_login(self, login_time):
        self.login_history.append(login_time)
        self.last_login = login_time

    def add_playtime(self, duration):
        self.playtime += duration

    def add_friend(self, friend):
        if friend not in self.friends_list:
            self.friends_list.append(friend)
            friend.add_friend(self)

    def add_payment(self, amount, date):
        self.payment_history.append({'amount': amount, 'date': date})
        self.total_spent += amount

    def join_guild(self, guild):
        if self.guild:
            self.leave_guild()
        self.guild = guild
        guild.add_member(self)

    def leave_guild(self):
        if self.guild:
            self.guild.remove_member(self)
            self.guild = None

    def gain_experience(self, amount):
        self.experience += amount
        while self.experience >= self.level * 100:
            self.level_up()

    def level_up(self):
        self.experience -= self.level * 100
        self.level += 1
        print(f"{self.name} leveled up to level {self.level}!")

    def add_to_inventory(self, item):
        self.inventory.append(item)
        self.update_gear_score()

    def update_gear_score(self):
        self.gear_score = sum(item.gear_score for item in self.inventory if isinstance(item, Equipment))

class Guild:
    def __init__(self, guild_id, name):
        self.guild_id = guild_id
        self.name = name
        self.members = []
        self.leader = None

    def add_member(self, player):
        if player not in self.members:
            self.members.append(player)
            player.guild = self
            if not self.leader:
                self.set_leader(player)

    def remove_member(self, player):
        if player in self.members:
            self.members.remove(player)
            player.guild = None
            if player == self.leader:
                self.set_leader(self.members[0] if self.members else None)

    def set_leader(self, player):
        if player in self.members:
            self.leader = player

class GameModeType(Enum):
    PVE = "Player vs Environment"
    PVP = "Player vs Player"
    RAID = "Raid"

class GameMode:
    def __init__(self, mode_name, mode_type):
        self.mode_name = mode_name
        self.mode_type = mode_type
        self.active_sessions = {}
        self.activity_logger = None

    def set_activity_logger(self, activity_logger):
        self.activity_logger = activity_logger

    def start_session(self, player):
        if player.player_id not in self.active_sessions:
            self.active_sessions[player.player_id] = datetime.now()
            print(f"{player.name} started a {self.mode_name} session.")
            if self.activity_logger:
                self.activity_logger.log_login(player)

    def end_session(self, player):
        if player.player_id in self.active_sessions:
            start_time = self.active_sessions.pop(player.player_id)
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds() / 60
            player.add_playtime(duration)
            self.award_experience(player, duration)
            print(f"{player.name} ended their {self.mode_name} session. Playtime: {duration:.2f} minutes.")
            if self.activity_logger:
                self.activity_logger.log_playtime(player, duration)
                self.activity_logger.log_game_session(player, self, duration)
                self.activity_logger.log_logout(player)

    def award_experience(self, player, duration):
        experience = int(duration * 10)  # 10 XP per minute
        player.gain_experience(experience)
        print(f"{player.name} gained {experience} experience.")

class Item:
    def __init__(self, name, item_type):
        self.name = name
        self.item_type = item_type

class Equipment(Item):
    def __init__(self, name, item_type, gear_score):
        super().__init__(name, item_type)
        self.gear_score = gear_score

class ActivityLogger:
    def __init__(self, data_warehouse):
        self.data_warehouse = data_warehouse

    def log_login(self, player):
        login_time = datetime.now()
        player.add_login(login_time)
        self.data_warehouse.store_player_data(player.player_id, {
            'event_type': 'login',
            'timestamp': login_time
        })

    def log_logout(self, player):
        logout_time = datetime.now()
        self.data_warehouse.store_player_data(player.player_id, {
            'event_type': 'logout',
            'timestamp': logout_time
        })

    def log_playtime(self, player, duration):
        player.add_playtime(duration)
        self.data_warehouse.store_player_data(player.player_id, {
            'event_type': 'playtime',
            'duration': duration,
            'timestamp': datetime.now()
        })

    def log_payment(self, player, amount):
        payment_time = datetime.now()
        player.add_payment(amount, payment_time)
        self.data_warehouse.store_player_data(player.player_id, {
            'event_type': 'payment',
            'amount': amount,
            'timestamp': payment_time
        })

    def log_level_up(self, player):
        self.data_warehouse.store_player_data(player.player_id, {
            'event_type': 'level_up',
            'new_level': player.level,
            'timestamp': datetime.now()
        })

    def log_game_session(self, player, game_mode, duration):
        self.data_warehouse.store_player_data(player.player_id, {
            'event_type': 'game_session',
            'game_mode': game_mode.mode_name,
            'duration': duration,
            'timestamp': datetime.now()
        })

class DataWarehouse:
    def __init__(self):
        self.player_data = {}

    def store_player_data(self, player_id, data):
        if player_id not in self.player_data:
            self.player_data[player_id] = []
        self.player_data[player_id].append(data)

    def get_player_data(self, player_id):
        return self.player_data.get(player_id, [])

    def export_to_csv(self, filename):
        all_data = []
        for player_id, events in self.player_data.items():
            for event in events:
                event_data = event.copy()
                event_data['player_id'] = player_id
                all_data.append(event_data)
        
        df = pd.DataFrame(all_data)
        df.to_csv(filename, index=False)
        print(f"Data exported to {filename}")

# Example usage and simulation
if __name__ == "__main__":
    # Create data warehouse and activity logger
    data_warehouse = DataWarehouse()
    activity_logger = ActivityLogger(data_warehouse)

    # Create players
    player1 = Player(player_id="p001", name="Hero123")
    player2 = Player(player_id="p002", name="Warrior456")

    # Create a guild and add players
    guild1 = Guild(guild_id="g001", name="Knights of Python")
    player1.join_guild(guild1)
    player2.join_guild(guild1)

    # Create game modes
    pve_mode = GameMode("Dungeon Crawl", GameModeType.PVE)
    pvp_mode = GameMode("Arena Battle", GameModeType.PVP)

    # Set activity logger for game modes
    pve_mode.set_activity_logger(activity_logger)
    pvp_mode.set_activity_logger(activity_logger)

    # Add some equipment
    sword = Equipment("Excalibur", "Weapon", 50)
    armor = Equipment("Dragon Scale Armor", "Armor", 75)

    player1.add_to_inventory(sword)
    player1.add_to_inventory(armor)

    # Simulate player activities over a week
    simulation_days = 7
    start_date = datetime.now()

    for day in range(simulation_days):
        current_date = start_date + timedelta(days=day)
        
        # Simulate login and game sessions
        for player in [player1, player2]:
            login_time = current_date + timedelta(hours=np.random.randint(9, 22))
            pve_mode.start_session(player)
            pve_duration = np.random.randint(30, 180)
            time.sleep(0.1)  # Small delay to ensure unique timestamps
            pve_mode.end_session(player)

            # Simulate PvP session for some days
            if np.random.random() > 0.5:
                pvp_mode.start_session(player)
                pvp_duration = np.random.randint(15, 60)
                time.sleep(0.1)
                pvp_mode.end_session(player)

            # Simulate payments (less frequent)
            if np.random.random() > 0.8:
                payment_amount = np.random.choice([4.99, 9.99, 19.99])
                activity_logger.log_payment(player, payment_amount)

    # Export data to CSV
    data_warehouse.export_to_csv("player_activity_data.csv")

    # Display some stats
    for player in [player1, player2]:
        print(f"\nPlayer: {player.name}")
        print(f"Level: {player.level}")
        print(f"Experience: {player.experience}")
        print(f"Gear Score: {player.gear_score}")
        print(f"Guild: {player.guild.name if player.guild else 'None'}")
        print(f"Total Playtime: {player.playtime:.2f} minutes")
        print(f"Total Spent: ${player.total_spent:.2f}")
        print(f"Last Login: {player.last_login}")