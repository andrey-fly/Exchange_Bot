import os
import sqlite3
import time
from rate_processing import RateProcessing as RPClass


class CurrencyLevel:

    def __init__(self, rpclass: RPClass):
        self.conn = sqlite3.connect("currencies_db.db")
        self.cursor = self.conn.cursor()
        self.rpclass = rpclass
        self.keys_list = rpclass.get_keys()

    def set_level(self, user_id, key, level):
        self.cursor.execute('INSERT INTO currencies_levels VALUES (?, ?)',
                            (user_id, key, level))
        self.conn.commit()

    def run(self, upd_time):
        start_time = time.time() - upd_time
        while True:
            if (time.time() - start_time) < upd_time:
                continue
            else:
                start_time = time.time()
                db_exists = int(self.cursor.execute("""SELECT COUNT(name) 
                                                     FROM sqlite_master
                                                     WHERE type='table' 
                                                     AND name='currencies_levels'""").fetchone()[0])
                if db_exists:
                    for key in self.currencies_ref_dict:
                        self.cursor.execute('UPDATE updated_currencies SET curr_value = ? WHERE curr_code = ?',
                                            (self.get_rate(key), key))
                        self.conn.commit()
                else:
                    self.cursor.execute("""CREATE TABLE currencies_levels(
                                                                        user_id INT(30) PRIMARY KEY,
                                                                        curr_code VAR_CHAR(3),
                                                                        curr_level DECIMAL(10, 2)
                                                                        );""")
                    for key in self.currencies_ref_dict:
                        self.cursor.execute('INSERT INTO updated_currencies VALUES (?, ?)', (key, self.get_rate(key)))
                        self.conn.commit()
    # def result_comparison(self):
    #     self.rate_processing.get_rates()
    #     self.rate_processing.currencies_ref_dict_key = self.currency_dict_key
    #     if self.rate_processing.rate < self.my_level:
    #         return True
    #     else:
    #         return False
    #
    # def execute(self):
    #     while self.flag_on:
    #         time.sleep(1800)
    #         if self.result_comparison():
    #             self.unexecute()
    #             return False
    #
    # def unexecute(self):
    #     self.flag_on = False
