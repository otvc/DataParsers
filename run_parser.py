import argparse
import os

from pymongo import MongoClient

from Stroller import BaseStoller
from UFCParse import ParserUFCStats
from PEngine import UFCEngine

def output(uri, count):
    os.system('cls')
    print(count)

def run_engine(connection, dbname, saved):
    fight_page_graph = {
        'http://www.ufcstats.com/event-details':
            {
                'http://www.ufcstats.com/fight-details/': None
            },
        'http://www.ufcstats.com/statistics/events/completed?page=': None
    }
    fight_page_graph['http://www.ufcstats.com/statistics/events/completed?page='] = fight_page_graph
    
    transition_graph = {'http://www.ufcstats.com/statistics/events/completed': fight_page_graph}

    particular_attr = ['href', 'data-link']

    ufc_stoller = BaseStoller(transition_graph, particular_attr)
    ufc_parser = ParserUFCStats()

    mongo_client = MongoClient(connection)
    ufc_mongodb = mongo_client[dbname]
    collection_names = {'tournaments': 'Tournaments', 'fights':'Fights'}

    ufc_engine = UFCEngine(ufc_stoller, ufc_parser, ufc_mongodb, collection_names, is_saved=saved)
    ufc_engine.Run()
    mongo_client.close()


def get_settings():
    arg_getter = argparse.ArgumentParser(prog = "UFCParser", description = "It's program parse www.ufcstats.com")
    arg_getter.add_argument('--connection',
                             default = 'mongodb://localhost:27017',
                             help = 'connection uri to db',)
    arg_getter.add_argument('--dbname', default = 'StatsUFC')
    arg_getter.add_argument('-s', '--saved', dest='saved',default=False)
    args = arg_getter.parse_args()
    return args.connection, args.dbname, args.saved

if __name__ == '__main__':
    connection, dbname, saved =  get_settings()
    run_engine(connection, dbname, saved)


