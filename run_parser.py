import argparse
import os
import yaml

from pymongo import MongoClient

from model import DBWrapper

from model.Stroller import BaseStoller, BaseFilter
from model.BaseParse import ParserUFCStats, ParserConsult, ParserYuristOnline
from model.PEngine import UFCEngine, ConsultEngine, YuristOnlineEngine

def output(uri, count):
    os.system('cls')
    print(count)

def select_db(mongo, collections, connection, dbname):
    if not mongo:
        mongodb = DBWrapper.KVDBCsv(connection, collections)
    else:
        mongodb = DBWrapper.KVDBMongo(connection, dbname, collections)
    return mongodb

def load_yalm_config(path):
    with open(path, 'r') as f_yaml:
        config = yaml.load(f_yaml)
    return config

def run_UFCStatsEngine(connection, dbname, saved, first_page, mongo):
    
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
    ufc_mongodb = select_db(mongo,collections, connection, dbname)

    ufc_engine = UFCEngine(ufc_stoller, ufc_parser, ufc_mongodb, collection_names, is_saved=saved)
    ufc_engine.Run()

def run_ConsultEngine(connection, dbname, saved, first_page, mongo):
    graph_parse = {
        'https://www.consultant.ru/popular/':
        {
            '/document/cons_doc':
            {
                '/document/cons_doc_LAW': None
            }
        }
    }
    filters = dict()
    filters['/document/cons_doc_LAW'] = BaseFilter(['Статья \d+'])
    particular_attr = ['href']
    stroller = BaseStoller(graph_parse, particular_attr, filters=filters)
    parser = ParserConsult()

    collections = ['CodesTypes', 'CodesTree', 'CodesParagraphs']
    collection_names = {'CodesTypes': 'CodesTypes', 'CodesTree':'CodesTree', 'CodesParagraphs': 'CodesParagraphs'}
    db = select_db(mongo, collections, connection, dbname)
    engine = ConsultEngine(stroller, parser, db, collection_names, is_saved=saved)
    engine.Run()

def run_YuristEngine(connection, dbname, saved, first_page, mongo):
    first_page = 'https://www.yurist-online.net/question/p/'
    graph_parse = {first_page + f'{page_num}':{'/question/': None} for page_num in range(55,11887)}

    filters = {}
    filters['/question/'] = BaseFilter(href_regex=['\/question\/\d+'])
    # filters['/question/p'] = BaseFilter(href_regex=['\/question\/p\/\d+'])

    particular_attr = ['href']
    stroller = BaseStoller(graph_parse, particular_attr, filters = filters)
    parser = ParserYuristOnline()
    collections = ['Questions', 'Answers']
    collection_names = {coll:coll for coll in collections}
    db = select_db(mongo, collections, connection, dbname)
    engine = YuristOnlineEngine(stroller, parser, db, collection_names, is_saved=saved)
    engine.Run()



def run_engine(parser, connection, dbname, saved, first_page, mongo):
    map_parser_run = {'ufcstats': run_ConsultEngine, 'consult': run_ConsultEngine, 'yurist-online': run_YuristEngine}
    engine_args = connection, dbname, saved, first_page, mongo
    map_parser_run[parser](*engine_args)


def get_settings():
    arg_getter = argparse.ArgumentParser(prog = "UFCParser", description = "It's program parse www.ufcstats.com")
    arg_getter.add_argument('-c','--connection',
                             default = 'mongodb://localhost:27017',
                             help = 'connection uri to db or file to dir if you want save to csv',)
    arg_getter.add_argument('-d', '--dbname', default = 'StatsUFC', help='name of database in mongo')
    arg_getter.add_argument('-s', '--saved', dest='saved', action='store_true', help='indicates that parser condition was saved')
    arg_getter.add_argument('-fp', '--first_page', default = 'http://www.ufcstats.com/statistics/events/completed')
    arg_getter.add_argument('-m', action = 'store_true', dest = 'mongo', help = 'if you don\'t want save in csv')
    
    parsers = ['ufcstats', 'consult', 'yurist-online']
    arg_getter.add_argument('-p', '--parsers', choices=parsers, default='yurist-online')

    args = arg_getter.parse_args()

    if not args.mongo and args.connection.startswith('mongodb'):
        args.connection = '.'

    return args.connection, args.dbname, args.saved, args.first_page, args.mongo, args.parsers

if __name__ == '__main__':
    connection, dbname, saved, first_page, mongo, parser =  get_settings()
    run_engine(parser, connection, dbname, saved, first_page, mongo)

