import sys
sys.path.append('../StatsUFC/model')

from pathlib import Path

import pandas
import DBWrapper

def test_KVDBCsv():
    path = 'tests\\Databases'
    collections = ['collection1']
    collumns = ['a', 'b']
    database = DBWrapper.KVDBCsv(path, collections = collections)
    data = {coll: coll + '_' + str(value) for value in range(100) for coll in collumns}
    database.insert_one(collections[0], data)
    file_path = Path(path + '/' + collections[0] + '.csv')
    assert file_path.is_file()

if __name__ == '__main__':
    test_KVDBCsv()