from commands.client import ClientCommand
from commands.say import SayCommand
from events import Event
from messages import SayText2
from paths import PLUGIN_DATA_PATH
from players.dictionary import PlayerDictionary
from players.helpers import index_from_userid
from players.helpers import playerinfo_from_index
from translations.strings import LangStrings

from bank.database import Database
from bank.player import Player
from bank.utils import KeyDefaultDict

# Globals
_database = None
_messages = None
players = None


def load():
    """Open the database and create player dictionary."""
    global _database, _messages, players
    _database = Database(PLUGIN_DATA_PATH / 'bank.sql')
    lang_strings = LangStrings('bank')
    _messages = KeyDefaultDict(lambda key: SayText2(lang_strings[key]))
    players = PlayerDictionary(_init_player)


def unload():
    """Close the database."""
    _database.close()


def _init_player(index):
    """Initialize a bank player from an index."""
    steamid = playerinfo_from_index(index).steamid
    balance = _database.load_balance(steamid)
    if balance is not None:
        _messages['Welcome Back'].send(index, balance=balance)
    else:
        balance = 0
    return Player(index, balance=balance)


@ClientCommand('balance')
@SayCommand('balance')
def _deposit_command(command, player_index, team_only=None):
    """Callback for player's check balance command."""
    if len(command) != 1:
        return
    player = players[player_index]
    _messages['View Balance'].send(player_index, balance=player.balance)


@ClientCommand('deposit')
@SayCommand('deposit')
def _deposit_command(command, player_index, team_only=None):
    """Callback for player's deposit command."""
    if len(command) != 2:
        return
    try:
        amount = int(command[1])
    except ValueError:
        _messages['Deposit Failure'].send(player_index, value=command[1])
    else:
        player = players[player_index]
        player.deposit(amount)
        _messages['Deposit Success'].send(player_index, amount=amount, balance=player.balance)


@ClientCommand('withdraw')
@SayCommand('withdraw')
def _withdraw_command(command, player_index, team_only=None):
    """Callback for player's withdraw command."""
    if len(command) != 2:
        return
    try:
        amount = int(command[1])
    except ValueError:
        _messages['Withdraw Failure'].send(player_index, value=command[1])
    else:
        player = players[player_index]
        player.withdraw(amount)
        _messages['Withdraw Success'].send(player_index, amount=amount, balance=player.balance)


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
    if index not in players:
        return
    player = players[index]
    with _database as db:
        db.save_balance(player.steamid, player.balance)
    del players[index]
