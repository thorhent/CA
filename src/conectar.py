import sys

import sqlite3

class Connect:

    def conectar(self):
        with sqlite3.connect(database='/home/thorhent/Projects/ClinicalAyudante/src/CAsqlite.db') as conn:
            cursor = conn.cursor()

        return cursor

    
