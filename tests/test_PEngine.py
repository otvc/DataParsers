import sys
sys.path.append('../StatsUFC/model')

from PEngine import ConsultEngine
from PEngine import YuristOnlineEngine
from DBWrapper import KVDBCsv
from BaseParse import ParserConsult
from BaseParse import ParserYuristOnline
from Stroller import BaseStoller

from TestHelper import get_gt_dirty_json
from TestHelper import ComparingDicts

def test_ConvertTreeToTable():
    gt_json, data = get_gt_dirty_json('tests/Data/GroundTruth/ConvertTreeToTable.json',
        'tests/Data/Dirty/ConvertTreeToTable.json')
    output = {'Id': [], 'Parent': [], 'Name': []}
    ConsultEngine.ConvertTreeToTable(data, output)
    assert all(ComparingDicts(gt_json, output))

def CreateConsultEngine():
    collections = dict()
    collections['CodesTypes'] = 'Codes_Test'
    collections['CodesTree'] = 'CodestTree_Test'
    collections['CodesParagraphs'] = 'Paragraphs_Test'
    db = KVDBCsv('tests\\Databases', collections = list(collections.values()))
    bs = BaseStoller(None, None, None)
    return ConsultEngine(bs, ParserConsult(), db, collections)

def CreateYouristOnlineEngine():
    collections = dict()
    collections['Questions'] = 'Questions_Test'
    collections['Answers'] = 'Answers_Test'
    db = KVDBCsv('tests\\Databases', collections = list(collections.values()))
    bs = BaseStoller(None, None, None)
    return YuristOnlineEngine(bs, ParserYuristOnline(), db, collections)

def test_TableOfContentHandler():
    ce = CreateConsultEngine()
    with open('tests/Pages/Consultant/NestedList.txt', 'r', encoding='utf-8') as f:
        doc = f.read()

    ce.TableOfContentHandler(doc)

def test_ArticleHandler():
    ce = CreateConsultEngine()
    with open('tests/Pages/Consultant/Docs/GetArticleAndName.html', 'r', encoding='utf-8') as f:
        doc = f.read()
    
    ce.ArticleHandler(doc)

def test_CodesHandler():
    ce = CreateConsultEngine()
    with open('tests/Pages/Consultant/Docs/GetAllPopularCodes.html', 'r', encoding='utf-8') as f:
        doc = f.read()
    
    ce.CodesHandler(doc)

def test_ListQuestionsHandler():
    ce = CreateYouristOnlineEngine()
    with open('tests/Pages/yurist-online/Docs/GetAllShortQuestions.html', 'r') as f:
        doc = f.read()
    
    ce.ListQuestionsHandler(doc)

def test_QuestionHandler():
    ce = CreateYouristOnlineEngine()
    with open('tests/Pages/yurist-online/Docs/QuestionPage.html', 'r') as f:
        doc = f.read()
    
    ce.QuestionHandler(doc, 'https://www.yurist-online.net/question/176711')

if __name__  == '__main__':
    test_ConvertTreeToTable()
    # test_TableOfContentHandler()
    # test_ArticleHandler()
    # test_CodesHandler()
    test_ListQuestionsHandler()
    test_QuestionHandler()
