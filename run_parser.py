import argparse
import os

from pymongo import MongoClient

import model.DBWrapper

from model.Stroller import BaseStoller
from model.BaseParse import ParserUFCStats
from model.PEngine import UFCEngine

def output(uri, count):
    os.system('cls')
    print(count)

def run_engine(connection, dbname, saved, first_page, mongo):
    
    fight_page_graph = {
        'http://www.ufcstats.com/event-details':
            {
                'http://www.ufcstats.com/fight-details/': None
            },
        'http://www.ufcstats.com/statistics/events/completed?page=': None
    }
    fight_page_graph['http://www.ufcstats.com/statistics/events/completed?page='] = fight_page_graph
    
    transition_graph = {first_page: fight_page_graph}

    particular_attr = ['href', 'data-link']

    ufc_stoller = BaseStoller(transition_graph, particular_attr)
    ufc_parser = ParserUFCStats()

    collections = ['Tournaments', 'Fights']
    collection_names = {'tournaments': 'Tournaments', 'fights':'Fights'}
    if not mongo:
        ufc_mongodb = DBWrapper.KVDBCsv(connection, collections)
    else:
        ufc_mongodb = DBWrapper.KVDBMongo(connection, dbname, collections)

    ufc_engine = UFCEngine(ufc_stoller, ufc_parser, ufc_mongodb, collection_names, is_saved=saved)
    ufc_engine.Run()


def get_settings():
    arg_getter = argparse.ArgumentParser(prog = "UFCParser", description = "It's program parse www.ufcstats.com")
    arg_getter.add_argument('-c','--connection',
                             default = 'mongodb://localhost:27017',
                             help = 'connection uri to db or file to dir if you want save to csv',)
    arg_getter.add_argument('-d', '--dbname', default = 'StatsUFC', help='name of database in mongo')
    arg_getter.add_argument('-s', '--saved', dest='saved', action='store_true', help='indicates that parser condition was saved')
    arg_getter.add_argument('-fp', '--first_page', default = 'http://www.ufcstats.com/statistics/events/completed')
    arg_getter.add_argument('-m', action = 'store_true', dest = 'mongo', help = 'if you don\'t want save in csv')

    args = arg_getter.parse_args()

    if not args.mongo and args.connection.startswith('mongodb'):
        args.connection = '.'

    return args.connection, args.dbname, args.saved, args.first_page, args.mongo

if __name__ == '__main__':
    connection, dbname, saved, first_page, mongo =  get_settings()
    run_engine(connection, dbname, saved, first_page, mongo)


