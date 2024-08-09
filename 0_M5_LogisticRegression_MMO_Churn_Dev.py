import pandas as pd
from datetime import datetime
import numpy as np
from enum import Enum

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

    def add_login(self, login_time):
        self.login_history.append(login_time)

    def add_playtime(self, duration):
        self.playtime += duration

    def add_friend(self, friend):
        if friend not in self.friends_list:
            self.friends_list.append(friend)
            friend.add_friend(self)

    def add_payment(self, amount, date):
        self.payment_history.append({'amount': amount, 'date': date})

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

    def start_session(self, player):
        if player.player_id not in self.active_sessions:
            self.active_sessions[player.player_id] = datetime.now()
            print(f"{player.name} started a {self.mode_name} session.")

    def end_session(self, player):
        if player.player_id in self.active_sessions:
            start_time = self.active_sessions.pop(player.player_id)
            duration = (datetime.now() - start_time).total_seconds() / 60
            player.add_playtime(duration)
            self.award_experience(player, duration)
            print(f"{player.name} ended their {self.mode_name} session. Playtime: {duration:.2f} minutes.")

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

# Example usage
if __name__ == "__main__":
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

    # Simulate game sessions
    pve_mode.start_session(player1)
    pvp_mode.start_session(player2)

    # Add some equipment
    sword = Equipment("Excalibur", "Weapon", 50)
    armor = Equipment("Dragon Scale Armor", "Armor", 75)

    player1.add_to_inventory(sword)
    player1.add_to_inventory(armor)

    # End sessions
    pve_mode.end_session(player1)
    pvp_mode.end_session(player2)

    # Display player info
    for player in [player1, player2]:
        print(f"\nPlayer: {player.name}")
        print(f"Level: {player.level}")
        print(f"Experience: {player.experience}")
        print(f"Gear Score: {player.gear_score}")
        print(f"Guild: {player.guild.name if player.guild else 'None'}")
        print(f"Playtime: {player.playtime:.2f} minutes")