import sqlite3


class DBManager:
    def __init__(self, db_path):
        self.conn = sqlite3.connect(db_path)
        self.cursor = self.conn.cursor()
        self._create_tables()

    def _create_tables(self):
        self.cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS players (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                won BOOLEAN
            )
        """
        )
        self.conn.commit()

    def add_player(self, name, won):
        try:
            self.cursor.execute(
                "INSERT INTO players (name, won) VALUES (?, ?)", (name, won)
            )
            self.conn.commit()
            db = self.cursor.execute("SELECT * FROM players")
            print(db.fetchall())
        except sqlite3.Error as e:
            print(f"An error occurred: {e}")


    def close_connection(self):
        self.conn.close()

    def get_win_lose_rate_for_name(self, name):
        try:
            self.cursor.execute(
                "SELECT COUNT(*) FROM players WHERE name = ? AND won = 1", (name,)
            )
            won = self.cursor.fetchone()[0]
            self.cursor.execute(
                "SELECT COUNT(*) FROM players WHERE name = ? AND won = 0", (name,)
            )
            lost = self.cursor.fetchone()[0]
            return won, lost
        except sqlite3.Error as e:
            print(f"An error occurred: {e}")