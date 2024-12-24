import sqlite3
import logging
from user_model import AuthModel

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",  # Custom format
)


class DatabaseClient:
    def __init__(self, db_name="./db/users.db"):
        logging.info("Connecting to the database...")
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()
        self.cursor.execute(""" 
            CREATE TABLE IF NOT EXISTS users (
                username TEXT PRIMARY KEY,
                password TEXT NOT NULL
            )
        """)
        self.conn.commit()
        logging.info("Database connection established and table created if not exists.")

    def user_exists(self, username):
        self.cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
        return self.cursor.fetchone() is not None

    def create_user(self, user_details: AuthModel):
        hashed_password = user_details.password  # Assume password is already hashed
        self.cursor.execute(
            "INSERT INTO users (username, password) VALUES (?, ?)",
            (user_details.username, hashed_password),
        )
        self.conn.commit()

    def get_user(self, username):
        self.cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
        return self.cursor.fetchone()

    def close(self):
        logging.info("Closing database connection...")
        self.conn.close()


def get_db():
    return DatabaseClient()
