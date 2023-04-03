import sqlite3 as sql


class DB:

    def __init__(self, db: str):
        self.db = sql.connect(db)
        self.cursor = self.db.cursor()

    def query(self, qr):
        self.cursor.execute(qr)
        self.db.commit()

    def return_query(self, qr):
        self.cursor.execute(qr)
        res = self.cursor.fetchall()
        return res

    def __del__(self):
        self.db.close()
