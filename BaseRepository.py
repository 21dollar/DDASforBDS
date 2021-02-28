from typing import Generator
import pyodbc

SERVER = 'LOCALHOST\\SQLEXPRESS'
DB_NAME = 'DDASforBDS'
DRIVER = '{SQL Server}'

DB_CONNECTION = pyodbc.connect(f'''
            Driver={DRIVER};
            Server={SERVER};
            Database={DB_NAME};
            Trusted_Connection=yes;''')
DB_CONNECTION.autocommit = True

class BaseDao:
    def dump(self): 
        return tuple()

class BaseRepository():
    TABLE_NAME = ''
    TABLE_PARAM = []
    BASE_TYPE = BaseDao

    def __init__(self):
        self.cursor = DB_CONNECTION.cursor()

    def queryForObject(self, sql, *args, wrapper=None):
        if not wrapper:
            return self.cursor.execute(sql, *args).fetchall()
        else:
            return [wrapper(*row) for row in self.cursor.execute(sql, *args)]

    def query(self, sql, *args):
        self.cursor.execute(sql, *args)

    def selectAll(self):
        query = f'''select {', '.join(self.TABLE_PARAM)} from {self.TABLE_NAME}'''
        data = self.queryForObject(query, wrapper=self.BASE_TYPE)
        return data

    def insert(self, data):
        query = f'''insert into {self.TABLE_NAME} VALUES ({', '.join('?' for _ in self.TABLE_PARAM)})'''
        if isinstance(data, self.BASE_TYPE):
            self.cursor.execute(query, data.dump())
        elif isinstance(data, Generator):
            self.cursor.executemany(query, [item.dump() for item in data])
        else:
            raise ValueError(f"Invalid data type, expected: {self.BASE_TYPE}")

    def count(self):
        query = f'''select count(*) from {self.TABLE_NAME}'''
        return self.cursor.execute(query).fetchone()[0]

    def clear(self):
        query = f'''truncate table {self.TABLE_NAME}'''
        self.cursor.execute(query)

    def __str__(self):
        return f"{self.TABLE_NAME} ({', '.join(self.TABLE_PARAM)}):\n" +\
            '\n'.join(str(item) for item in self.selectAll())