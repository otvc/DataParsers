import logging
from collections.abc import Callable

log_settings = { 
    'filemode': 'w', 'format':"%(asctime)s %(levelname)s %(message)s"
}

logging.basicConfig(filename = 'parser_error.log', level=logging.ERROR, **log_settings)
logging.basicConfig(filename = 'parser_warning.log', level=logging.WARNING, **log_settings)

from collections import defaultdict
import datetime

from DBWrapper import KVDBWrapper
from pymongo.database import Database

from Stroller import BaseStoller
from UFCParse import Parser
from UFCParse import ParserUFCStats

class ParserEngine:

    def __init__(self, stoller:BaseStoller, 
                       parser:Parser, 
                       database:KVDBWrapper,
                       collections:dict[str],
                       сur_pos_handler:Callable[[str, int]] = None,
                       is_saved = False,
                       path_to_save = 'viewed_pages.txt') -> None:
        self.stoller = stoller
        self.parser = parser
        self.database = database
        self.collections = collections
        self.cus_pos_handler = сur_pos_handler
        self.path_to_save = path_to_save
        self.stoller.setPageProcessed(self.HistoryCallback)
        if is_saved:
            self.LoadViewed()
        else:
            self.viewed_pages = {}
    
    def HistoryCallback(self, url, document):
        if self.cus_pos_handler:
            self.cus_pos_handler(url, len(self.viewed_pages))
        self.DocumentHandler(url, document)
        self.viewed_pages[url] = True

    def DocumentHandler(self, url, document):
        pass

    def Run(self):
        try:
            self.stoller.StartWandering()
        except Exception as e:
            logging.error(str(e))
    
    def SaveURI(self, uri):
        with open('viewed_pages.txt', 'a') as f:
            f.write(uri + '\n')
    
    def LoadViewed(self):
        with open('viewed_pages.txt', 'r') as f:
            pages = f.readlines()
        self.viewed_pages = dict.fromkeys(pages)


class UFCEngine(ParserEngine):

    def __init__(self, stoller: BaseStoller, 
                       parser:Parser, 
                       database: KVDBWrapper,
                       collections:dict[str],
                       cur_pos_handler: Callable[[str, int]] = None,
                       is_saved = False,
                       path_to_save = 'viewed_pages.txt') -> None:
        super().__init__(stoller, parser, database, collections, cur_pos_handler, is_saved, path_to_save)
        assert isinstance(parser, ParserUFCStats)
        self.tour_collection = collections['tournaments']
        self.fight_collection = collections['fights']
    
    def DocumentHandler(self, url:str, document):
        if url in self.viewed_pages:
            return
        if url.startswith('http://www.ufcstats.com/statistics/events/completed'):
            self.TournamentHandler(document)
        elif url.startswith('http://www.ufcstats.com/fight-details'):
            self.FightHandler(document)
    
    def TournamentHandler(self, document:str):
        tournaments = self.parser.GetTournaments(document)
        self.database.insert_many(self.tour_collection, tournaments)

    def FightHandler(self, document:str):
        try:
            fight_stats = self.parser.GetFightStats(document)
            self.database.insert_one(self.fight_collection, fight_stats)
        #Parser may have problems if tournament is empty
        except Exception as ae:
            logging.warning(str(ae))

