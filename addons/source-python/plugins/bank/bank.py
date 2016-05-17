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
import bank._globals as _globals


def load():
    """Initialize the variables in `_globals.py` on plugin load."""
    _globals.database = Database(PLUGIN_DATA_PATH / 'bank.sql')
    _globals.lang_strings = LangStrings('bank')
    _globals.messages = KeyDefaultDict(lambda key: SayText2(lang_strings[key]))
    _globals.players = PlayerDictionary(_init_player)


def unload():
    """Close the database on plugin unload."""
    _globals.database.close()


def _init_player(index):
    """Initialize a bank player from an index."""
    steamid = playerinfo_from_index(index).steamid
    balance = _database.load_balance(steamid)
    if balance is None:
        balance = 0
    return Player(index, balance=balance)


@ClientCommand('balance')
@SayCommand('balance')
def _deposit_command(command, player_index, team_only=None):
    """Callback for player's check balance command."""
    if len(command) != 1:
        return
    player = _globals.players[player_index]
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
        player = _globals.players[player_index]
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
        player = _globals.players[player_index]
        player.withdraw(amount)
        _messages['Withdraw Success'].send(player_index, amount=amount, balance=player.balance)


@Event('round_start')
def _on_round_start(event):
    """Save players' balance."""
    with _globals.database as db:
        for player in _globals.players.values():
            db.save_balance(player.steamid, player.balance)


@Event('player_disconnect')
def _on_player_disconnect(event):
    """Save player's balance."""
    index = index_from_userid(event['userid'])
    if index not in _globals.players:
        return
    player = _globals.players[index]
    with _globals.database as db:
        db.save_balance(player.steamid, player.balance)
    del _globals.players[index]
