from dataclasses import dataclass

class TableHistory:
    TABLE_NAME = "history"
    TABLE_HISTORY = """
    CREATE TABLE IF NOT EXISTS history (
     id INTEGER PRIMARY KEY, 
     command TEXT, 
     created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)
    """
    INSERT_HISTORY = "INSERT INTO history (command, created_at) VALUES (?, ?)"

    @dataclass
    class History:
        id: int
        name: str
        created_at: str


class TableUser:
    TABLE_NAME = "users"
    TABLE_USER = "CREATE TABLE IF NOT EXISTS users ( id INTEGER PRIMARY KEY, name TEXT, age INTEGER)"
    INSERT_USER = "INSERT INTO users (name, age) VALUES (?, ?)"

