from commands.client import ClientCommand
from commands.say import SayCommand
from events import Event
from paths import PLUGIN_DATA_PATH
from players.dictionary import PlayerDictionary
from players.helpers import index_from_userid
from players.helpers import playerinfo_from_index

from bank.database import Database
from bank.player import Player

# Globals
_database = None
players = None


def load():
    """Open the database and create player dictionary."""
    _database = Database(PLUGIN_DATA_PATH / 'bank.sql')
    players = PlayerDictionary(_init_player)


def unload():
    """Close the database."""
    _database.close()


def _init_player(index):
    """Initialize a bank player from an index."""
    steamid = playerinfo_from_index(index).steamid
    balance = _database.load_balance(steamid)
    if balance is None:
        balance = 0
    return Player(index, balance=balance)


@ClientCommand('deposit')
@SayCommand('deposit')
def _deposit_command(command, player_index, team_only=None):
    """Callback for player's deposit command."""
    if len(command) != 2:
        return
    try:
        amount = int(command[1])
    except ValueError:
        return
    players[player_index].deposit(amount)


@ClientCommand('withdraw')
@SayCommand('withdraw')
def _withdraw_command(command, player_index, team_only=None):
    """Callback for player's withdraw command."""
    if len(command) != 2:
        return
    try:
        amount = int(command[1])
    except ValueError:
        return
    players[player_index].withdraw(amount)


@Event('round_start')
def _on_round_start(event):
    """Save players' balance."""
    with _database as db:
        for player in players.values():
            db.save_balance(player.steamid, player.balance)


@Event('player_disconnect')
def _on_player_disconnect(event):
    """Save player's balance."""
    index = index_from_userid(event['userid'])
    player = players[index]
    with _database as db:
        db.save_balance(player.steamid, player.balance)
    del players[index]
