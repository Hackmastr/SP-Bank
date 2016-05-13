from players.entity import Player as SourcePythonPlayer


class Player(SourcePythonPlayer):
    """Player with bank balance and deposit/withdraw functionality."""

    def __init__(self, *args, balance=0, **kwargs):
        """Initialize the player with an initial balance."""
        super().__init__(*args, **kwargs)
        self._balance = balance

    @property
    def balance(self):
        """Player's current bank balance."""
        return self._balance
    
    def deposit(self, amount):
        """Deposit cash to player's bank.

        Will deposit everything if amount is more than player has.
        """
        amount = min(amount, self.cash)
        self._balance += amount
        self.cash -= amount

    def withdraw(self, amount):
        """Withdraw cash from player's bank.

        Will withdraw everything if amount is more than player has.
        """
        amount = min(amount, self.balance)
        self.cash += amount
        self._balance -= amount
