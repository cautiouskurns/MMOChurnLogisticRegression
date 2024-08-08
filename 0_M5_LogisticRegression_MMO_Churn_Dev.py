# Imports necessary for the entire project
import pandas as pd
from datetime import datetime
import numpy as np

# Future imports (machine learning models, data processing)
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, roc_auc_score, confusion_matrix

class Player:
    def __init__(self, player_id, name, level=1, gear_score=0):
        """
        Initialize a Player object with basic attributes.

        Parameters:
        player_id (str): Unique identifier for the player.
        name (str): Name of the player.
        level (int): Player's current level.
        gear_score (int): Player's current gear score.
        """
        self.player_id = player_id
        self.name = name
        self.level = level
        self.gear_score = gear_score
        self.achievements = []
        self.login_history = []
        self.playtime = 0
        self.friends_list = []
        self.payment_history = []

    def add_login(self, login_time):
        """Log a player's login time."""
        self.login_history.append(login_time)

    def add_playtime(self, duration):
        """Add playtime to the player's total playtime."""
        self.playtime += duration

    def add_friend(self, friend):
        """Add a friend to the player's friend list."""
        self.friends_list.append(friend)

    def add_payment(self, amount, date):
        """Log a payment made by the player."""
        self.payment_history.append({'amount': amount, 'date': date})


class Guild:
    def __init__(self, guild_id, name):
        """
        Initialize a Guild object.

        Parameters:
        guild_id (str): Unique identifier for the guild.
        name (str): Name of the guild.
        """
        self.guild_id = guild_id
        self.name = name
        self.members = []

    def add_member(self, player):
        """Add a player to the guild."""
        self.members.append(player)

    def remove_member(self, player):
        """Remove a player from the guild."""
        self.members.remove(player)


if __name__ == "__main__":
    # Create a new player
    player1 = Player(player_id="p001", name="Hero123")
    player1.add_login(datetime.now())
    player1.add_playtime(120)  # Add 2 hours of playtime
    player1.add_payment(9.99, datetime.now())

    # Create a guild and add the player to it
    guild1 = Guild(guild_id="g001", name="Knights of Python")
    guild1.add_member(player1)

    # Display basic player info
    print(f"Player: {player1.name}, Level: {player1.level}, Playtime: {player1.playtime} minutes")
    print(f"Guild: {guild1.name}, Members: {[member.name for member in guild1.members]}")

