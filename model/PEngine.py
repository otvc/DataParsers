import sys
sys.path.append('../StatsUFC/model')

import logging
from collections.abc import Callable
from run_parser import log_settings

logging.basicConfig(filename = 'parser_error.log', level=logging.ERROR, **log_settings)
logging.basicConfig(filename = 'parser_warning.log', level=logging.WARNING, **log_settings)

from collections import defaultdict
import datetime
import re

from DBWrapper import KVDBWrapper
from pymongo.database import Database

from Stroller import BaseStoller
from BaseParse import Parser
from BaseParse import ParserUFCStats
from BaseParse import ParserConsult
from BaseParse import ParserYuristOnline

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
        self.current_url = None
        if is_saved:
            self.LoadViewed()
        else:
            self.viewed_pages = {}
    
    def HistoryCallback(self, url, document):
        self.current_url = url
        if self.cus_pos_handler:
            self.cus_pos_handler(url, len(self.viewed_pages))
        self.DocumentHandler(url, document)
        self.viewed_pages[url] = True

    def DocumentHandler(self, url, document):
        pass

    def Run(self):
        try:
            self.stoller.StartWandering()
        except AttributeError as ae:
            logging.error(str(ae))
        except IndexError as index_error:
            logging.error(str(index_error))
            logging.error(self.current_url)
    
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
        # assert isinstance(parser, ParserUFCStats)
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
            logging.warning(ae)


class ConsultEngine(ParserEngine):

    def __init__(self, stoller: BaseStoller, 
                       parser: Parser,
                       database: KVDBWrapper, 
                       collections: dict[str], 
                       сur_pos_handler: Callable[[str, int]] = None, 
                       is_saved=False, 
                       path_to_save='viewed_pages.txt') -> None:
        super().__init__(stoller, parser, database, collections, сur_pos_handler, is_saved, path_to_save)
        # assert isinstance(parser, ParserConsult)
        self.reg_toc =  'https:\/\/www\.consultant\.ru\/document\/\w*\/'# for table of content
        self.reg_article = 'https:\/\/www\.consultant\.ru\/document\/\w*\/\w*\/'
        self.codes_types_coll = self.collections['CodesTypes']
        self.codes_tree_coll = self.collections['CodesTree']
        self.codes_par_coll = self.collections['CodesParagraphs']

    
    def DocumentHandler(self, url:str, document):
        if url in self.viewed_pages:
            return
        if url.startswith('https://www.consultant.ru/popular/'):
            self.CodesHandler(document)
        elif re.match(self.reg_article, url):
            self.ArticleHandler(document)
        elif re.match(self.reg_toc, url):
            self.TableOfContentHandler(document)
    
    def CodesHandler(self, doc):
        codes_types = self.parser.GetAllPopularCodes(doc)
        try:
            last_id = self.database.get_last_index(self.codes_types_coll, index_col = 'Id')
        except FileNotFoundError:
            last_id = 0
        
        codes_types_format = {'Id': [], 'Parent': [], 'Name': []}
        ConsultEngine.ConvertTreeToTable(codes_types, codes_types_format, current_id = last_id, parent = -1)
        self.database.insert_many(self.codes_types_coll, codes_types_format)
        

    def TableOfContentHandler(self, doc):
        tree_of_content = self.parser.GetCodesTree(doc)
        try:
            last_id = self.database.get_last_index(self.codes_tree_coll, index_col = 'Id')
        except FileNotFoundError:
            last_id = 0

        content_table_format = {'Id': [], 'Parent': [], 'Name': []}
        ConsultEngine.ConvertTreeToTable(tree_of_content, content_table_format, current_id = last_id, parent = -1)
        
        self.database.insert_many(self.codes_tree_coll, content_table_format)

    def ArticleHandler(self, doc):
        paragraphs = self.parser.GetArticleAndName(doc)

        
        art_idx = self.database.get_index_by_value(self.codes_tree_coll, 
                                                   column_name='Name',
                                                   value = paragraphs['Name'],
                                                   index_col = 'Id')
        try:
            last_id = self.database.get_last_index(self.codes_types_coll, index_col = 'Id')
        except FileNotFoundError:
            last_id = 0

        table_paragraphs = dict()
        count_paragraphs = len(paragraphs['Paragraphs'])
        table_paragraphs['Id'] = []
        table_paragraphs['Id'].extend(range(last_id, last_id + count_paragraphs))
        table_paragraphs['Paragraph'] = paragraphs['Paragraphs']
        table_paragraphs['Article_Id'] = [art_idx] * count_paragraphs

        self.database.insert_many(self.codes_par_coll, table_paragraphs)
    
    '''
    Convert Tree to comfortable format
    '''
    def ConvertTreeToTable(nodes, output, current_id = 0, parent = -1, 
                           parent_col = 'Parent', name_col = 'Name', index_col = 'Id'):
        is_dict = isinstance(nodes, dict)
        names = list(nodes.keys()) if is_dict else nodes
        
        nodes_count = len(names)

        output[name_col].extend(names)

        parents = [parent] * nodes_count
        output[parent_col].extend(parents) 

        indeces = range(current_id, current_id + nodes_count)
        output[index_col].extend(indeces)

        current_id = current_id + nodes_count

        if is_dict:
            for parent_id, name in enumerate(names, start= current_id - nodes_count):
                current_id = ConsultEngine.ConvertTreeToTable(nodes[name],
                                                              parent = parent_id,
                                                              current_id = current_id, 
                                                              output = output)
        
        return current_id


class YuristOnlineEngine(ParserEngine):

    def __init__(self, 
                 stoller: BaseStoller, 
                 parser: Parser, 
                 database: KVDBWrapper, 
                 collections: dict[str], 
                 сur_pos_handler: Callable[[str, int]] = None,
                 is_saved=False, 
                 path_to_save='viewed_pages.txt') -> None:
        super().__init__(stoller, parser, database, collections, сur_pos_handler, is_saved, path_to_save)
        # assert isinstance(parser, ParserYuristOnline)
        self.reg_quest = re.compile('https:\/\/www\.yurist-online\.net\/question\/\d+')
        self.reg_digits = re.compile('\d+')
        self.quest_coll = collections['Questions']
        self.answers_coll = collections['Answers']
        

    def DocumentHandler(self, url:str, document):
        if url in self.viewed_pages:
            return
        if re.match(self.reg_quest, url):
            self.QuestionHandler(document, url)
        elif url == 'https://www.yurist-online.net/question' or \
             url.startswith('https://www.yurist-online.net/question/p'):
            self.ListQuestionsHandler(document)
            
    def QuestionHandler(self, doc, url):
        question, answers = self.parser.GetQuestAndAnswers(doc)

        id = int(re.search(self.reg_digits, url).group())
        for answer in answers:
            answer["QuestionId"] = id

        self.database.insert_value_by_index(self.quest_coll, 'Text', question, id)
        self.database.insert_many(self.answers_coll, answers)
    
    def ListQuestionsHandler(self, doc):
        questions = self.parser.GetAllShortQuestions(doc)
        for question in questions:
            question['Text'] = ""
        self.database.insert_many(self.quest_coll, questions, index_col = "Id")
    
    