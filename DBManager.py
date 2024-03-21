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
                game_index INTEGER,
                won BOOLEAN,
                score INTEGER
            )
            """
        )
        self.conn.commit()

    def add_player(self, name, won, score):
        try:
            # Check the current index for the player
            self.cursor.execute(
                "SELECT MAX(game_index) FROM players WHERE name = ?", (name,)
            )
            result = self.cursor.fetchone()
            current_index = 1 if result[0] is None else result[0] + 1

            # Insert the new record
            self.cursor.execute(
                "INSERT INTO players (name, game_index, won, score) VALUES (?, ?, ?, ?)",
                (name, current_index, won, score),
            )
            self.conn.commit()
        except sqlite3.Error as e:
            print(f"An error occurred: {e}")

    def get_matches_for_name(self, name):
        try:
            self.cursor.execute(
                "SELECT name, game_index, won, score FROM players WHERE name = ?",
                (name,),
            )
            return self.cursor.fetchall()
        except sqlite3.Error as e:
            print(f"An error occurred: {e}")
            return []

    def add_game(self, name, score):
        self.add_player(name, True, score)

    def close_connection(self):
        self.conn.close()
