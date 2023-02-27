from pathlib import Path
from pymongo import MongoClient
import pandas as pd

class KVDBWrapper:
    
    def __init__(self, connection, dbname, collections) -> None:
        self.connection = connection
        self.dbname = dbname
        self.collections = collections
    
    def insert_one(self, coll_name, data, index_col='Id'):
        pass
    
    def insert_many(self, coll_name, data, index_col='Id'):
        pass
    
    def insert_value_by_index(self, coll_name, column, value, index, index_col = 'Id'):
        pass

    def get_last_index(self, coll_name, column_name, value, index_col='Id'):
        pass

    def get_index_by_value(self, coll_name, column_name, value, index_col = 'Id'): 
        pass

class KVDBMongo(KVDBWrapper):
    
    def __init__(self, connection, dbname, collections) -> None:
        super().__init__(connection, dbname, collections)
        self.mongo_client = MongoClient(connection)
        self.database = self.mongo_client[dbname]
    
    def insert_one(self, coll_name, data):
        return self.database[coll_name].insert_one(data)

    def insert_many(self, coll_name, data):
        return self.database[coll_name].insert_many(data)
    
    def __del__(self):
        self.mongo_client.close()

class KVDBCsv(KVDBWrapper):

    def __init__(self, connection, collections, dbname = None) -> None:
        super().__init__(connection, dbname, collections)

    def insert_one(self, coll_name, data, index_col = 'Id'):
        self.insert_many(coll_name, [data], index_col=index_col)
    
    def insert_many(self, coll_name, data, index_col = None):
        if coll_name in self.collections:
            path = Path(self.__create_source(coll_name))
            header = not path.is_file()
            coll_df = pd.DataFrame(data)
            if index_col:
                coll_df.set_index(index_col,inplace=True)
            with open(path, 'a', encoding="utf-8") as fp:
                coll_df.to_csv(fp, header = header)

    def insert_value_by_index(self, coll_name, column, value, index, index_col = 'Id'):
        #NOT OPTIMAL!
        path = Path(self.__create_source(coll_name))
        collection = pd.read_csv(path, index_col=index_col)
        collection.loc[collection.index == index, column] = value
        collection.to_csv(path)

    def get_last_index(self, coll_name, index_col = 'Unnamed: 0'):
        #Not optimal!
        path = Path(self.__create_source(coll_name))
        if path.is_file():
            collection = pd.read_csv(path, index_col=index_col)
            if collection.index.empty:
                index = -1
            else:
                index = collection.index.values.max()
        else:
            raise FileNotFoundError()
        return index

    def get_index_by_value(self, coll_name, column_name, value, index_col = 'Id'): 
        path = Path(self.__create_source(coll_name))
        collection = pd.read_csv(path, index_col=index_col)
        indeces = collection[collection[column_name] == value].index
        if indeces.empty:
            index = -1
        else:
            index = indeces[-1]
        return index
    
    def __create_source(self, collection):
        return self.connection + collection + '.csv'


    