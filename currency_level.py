import sqlite3
from rate_processing import RateProcessing as RPClass


class CurrencyLevel:

    def __init__(self, rpclass: RPClass):
        self.conn = sqlite3.connect("currencies_db.db")
        self.cursor = self.conn.cursor()
        self.rpclass = rpclass
        self.keys_list = rpclass.currencies_ref_dict.keys()
        self.users_to_send = {}

    def set_level(self, user_id, key, level):
        self.cursor.execute('INSERT INTO currencies_levels VALUES (?, ?, ?)',
                            (user_id, key, level))
        self.conn.commit()

    def output(self):
        self.cursor.execute('SELECT * FROM currencies_levels')
        print(self.cursor.fetchall())

    def get_id_to_send(self, key):
        self.cursor.execute('SELECT user_id, curr_value '
                            'FROM currencies_levels '
                            'WHERE curr_value <= (SELECT curr_value'
                            '                     FROM updated_currencies'
                            '                     WHERE curr_code = (?)) '
                            'AND curr_code = (?)', (key, key))

        # self.cursor.execute('SELECT curr_value FROM updated_currencies WHERE curr_code = (?)', (key,))
        self.users_to_send[key] = [item for item in self.cursor.fetchall()]
        for item in [item[0] for item in self.users_to_send[key]]:
            self.cursor.execute('DELETE FROM currencies_levels '
                                'WHERE user_id = (?) AND curr_code = (?)', (item, key))
        self.conn.commit()

    def execute(self):
        for key in self.keys_list:
            self.get_id_to_send(key)

# CLClass = CurrencyLevel(RPClass())
# CLClass.execute()
# print(CLClass.users_to_send)
# CurrencyLevel(RPClass()).output()
