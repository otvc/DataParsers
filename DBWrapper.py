from pathlib import Path
from pymongo import MongoClient
import pandas

class KVDBWrapper:
    
    def __init__(self, connection, dbname, collections) -> None:
        self.connection = connection
        self.dbname = dbname
        self.collections = collections
    
    def insert_one(self, coll_name, data):
        pass

    def insert_many(self, coll_name, data):
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

    def insert_one(self, coll_name, data):
        self.insert_many(coll_name, [data])
    
    def insert_many(self, coll_name, data):
        if coll_name in self.collections:
            path = Path(self.__create_source(coll_name))
            header = not path.is_file()
            coll_df = pandas.DataFrame(data)
            with open(path, 'a') as fp:
                coll_df.to_csv(fp, header = header)
    
    def __create_source(self, collection):
        return self.connection + '\\' + collection + '.csv'


    