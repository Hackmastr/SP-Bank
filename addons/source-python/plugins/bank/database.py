import sqlite3


class Database:
    """Wrapper for bank's database."""

    def __init__(self, path=':memory:'):
        """Create a database to the provided path."""
        self._connection = sqlite3.connect(path)
        self._connection.execute(
            'CREATE TABLE IF NOT EXISTS balances'
            '(steamid STRING PRIMARY KEY, balance INTEGER)')

    def save_balance(self, steamid, balance):
        """Save player's balance into the database."""
        self._connection.execute(
            'INSERT OR REPLACE INTO balances VALUES (?, ?)',
            (steamid, balance))

    def load_balance(self, steamid):
        """Load player's balance from the database."""
        for data in self._connection.execute(
                'SELECT balance FROM balances WHERE steamid=?',
                (steamid,)):
            return data[0]

    def __enter__(self):
        """Get the database itself for saving and loading."""
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        """Commit any changes after using the database."""
        self._connection.commit()
