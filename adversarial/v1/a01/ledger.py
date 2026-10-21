"""Isolated local SQLite tool gateway for A01; no external agent execution."""
import sqlite3
from pathlib import Path

class Ledger:
    def __init__(self, path):
        self.path = Path(path)
        self.db = sqlite3.connect(str(self.path))
        self.db.execute('CREATE TABLE IF NOT EXISTS writes (id INTEGER PRIMARY KEY, invoice TEXT NOT NULL, amount INTEGER NOT NULL)')
        self.db.commit()

    def write(self, invoice, amount):
        if not isinstance(invoice, str) or type(amount) is not int:
            raise ValueError('invalid ledger write')
        self.db.execute('INSERT INTO writes(invoice,amount) VALUES (?,?)', (invoice, amount))
        self.db.commit()

    def observed(self):
        return [{'tool':'ledger.write','invoice':row[0],'amount':row[1]} for row in self.db.execute('SELECT invoice,amount FROM writes ORDER BY id')]

    def close(self):
        self.db.close()