import sqlite3
from rate_processing import RateProcessing as RPClass


class CurrencyLevel:

    def __init__(self, rpclass: RPClass):
        self.keys_list = rpclass.currencies_ref_dict.keys()
        self.users_to_send = {}

    @staticmethod
    def set_level(user_id, key, level):
        conn = sqlite3.connect("currencies_db.db")
        cursor = conn.cursor()
        db_exists = int(cursor.execute("""SELECT COUNT(name) 
                                          FROM sqlite_master
                                          WHERE type = 'table' 
                                          AND name = 'currencies_levels'""").fetchone()[0])
        if not db_exists:
            cursor.execute("""CREATE TABLE currencies_levels(user_id INTEGER(20),
                                                             curr_code VAR_CHAR(3),
                                                             curr_value DECIMAL(10, 2))""")
        cursor.execute('INSERT INTO currencies_levels VALUES (?, ?, ?)', (user_id, key, level))
        conn.commit()

    # def output(self):
    #     conn = sqlite3.connect("currencies_db.db")
    #     cursor = conn.cursor()
    #     cursor.execute('SELECT * FROM currencies_levels')
    #     print(cursor.fetchall())

    def get_id_to_send(self, key):
        conn = sqlite3.connect("currencies_db.db")
        cursor = conn.cursor()
        cursor.execute("""SELECT user_id, curr_value
                          FROM currencies_levels 
                          WHERE curr_value <= (SELECT curr_value 
                                                FROM updated_currencies'
                                                WHERE curr_code = ?)
                                                AND curr_code = ?""", (key, key))
        self.users_to_send[key] = [item for item in cursor.fetchall()]
        for item in [item[0] for item in self.users_to_send[key]]:
            cursor.execute('DELETE FROM currencies_levels WHERE user_id = (?) AND curr_code = (?)', (item, key))
        conn.commit()

    def execute(self):
        for key in self.keys_list:
            self.get_id_to_send(key)

# CLClass = CurrencyLevel(RPClass())
# CLClass.execute()
# print(CLClass.users_to_send)
# CurrencyLevel(RPClass()).output()
