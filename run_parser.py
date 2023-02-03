import argparse
import os
import logging
import yaml
from yaml.loader import SafeLoader

from pymongo import MongoClient

from model import DBWrapper

from model.Stroller import BaseStoller, BaseFilter
from model.BaseParse import ParserUFCStats, ParserConsult, ParserYuristOnline
from model.PEngine import UFCEngine, ConsultEngine, YuristOnlineEngine

log_settings = { 
    'filemode': 'a', 'format':"%(asctime)s %(levelname)s %(message)s"
}

logging.basicConfig(filename = 'parser_error.log', level=logging.ERROR, **log_settings)
logging.basicConfig(filename = 'parser_warning.log', level=logging.WARNING, **log_settings)

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
        config = yaml.load(f_yaml, Loader=SafeLoader)
    return config

def run_UFCStatsEngine(settings):
    
    fight_page_graph = {
        'http://www.ufcstats.com/event-details':
            {
                'http://www.ufcstats.com/fight-details/': None
            },
        'http://www.ufcstats.com/statistics/events/completed?page=': None
    }
    fight_page_graph['http://www.ufcstats.com/statistics/events/completed?page='] = fight_page_graph
    
    transition_graph = {settings['base_source']: fight_page_graph}

    particular_attr = ['href', 'data-link']

    ufc_stoller = BaseStoller(transition_graph, particular_attr)
    ufc_parser = ParserUFCStats()

    collections = settings['collections']
    collection_names = {'tournaments': collections[0], 'fights': collections[1]}
    ufc_mongodb = select_db(settings['save_to_mongo'], collections, settings['connection'], settings['dbname'])

    ufc_engine = UFCEngine(ufc_stoller, ufc_parser, ufc_mongodb, collection_names, is_saved=settings['saved'])
    ufc_engine.Run()

def run_ConsultEngine(settings):
    graph_parse = settings['graph']
    filters = dict()
    filters['/document/cons_doc_LAW'] = BaseFilter(['Статья \d+'])
    particular_attr = ['href']
    stroller = BaseStoller(graph_parse, particular_attr, filters=filters)
    parser = ParserConsult()

    collections = settings['collections']
    collection_names = {'CodesTypes': collections[0], 'CodesTree':collections[1], 'CodesParagraphs': collections[2]}
    db = select_db(settings['save_to_mongo'], collections, settings['connection'], settings['dbname'])
    engine = ConsultEngine(stroller, parser, db, collection_names, is_saved=settings['saved'])
    engine.Run()

def run_YuristEngine(settings):
    first_page = settings['base_source']
    first_page_number, last_page_number = settings['first_page_number'], settings['last_page_number'] 
    graph_parse = {first_page + f'{page_num}':{'/question/': None} for page_num in range(first_page_number, last_page_number)}

    filters = {}
    filters['/question/'] = BaseFilter(href_regex=['\/question\/\d+'])

    collections = settings['collections']
    collection_names = {'Questions':collections[0], 'Answers': collections[1]}
    db = select_db(settings['save_to_mongo'], collections, settings['connection'], settings['dbname'])

    particular_attr = ['href']
    stroller = BaseStoller(graph_parse, particular_attr, filters = filters)
    parser = ParserYuristOnline()
    engine = YuristOnlineEngine(stroller, parser, db, collection_names, is_saved=settings['saved'])
    engine.Run()

def run_engine(parser, path_config):
    map_parser_run = {'ufcstats': run_UFCStatsEngine, 'consult': run_ConsultEngine, 'yurist-online': run_YuristEngine}
    config = load_yalm_config(path_config)
    map_parser_run[parser](config[parser])

def get_settings():
    arg_getter  = argparse.ArgumentParser(prog = 'DParser', description = "It's with different parsers")
    parsers = ['ufcstats', 'consult', 'yurist-online']
    arg_getter.add_argument('-p', '--parser', choices = parsers, default = parsers[1])
    arg_getter.add_argument('-c', '--config',  default='./config/config.yaml',  help='file with settings for parsers')

    args = arg_getter.parse_args()
    return args.parser, args.config

if __name__ == '__main__':
    parser, path_config =  get_settings()
    run_engine(parser, path_config)

