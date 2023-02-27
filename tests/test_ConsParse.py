import sys
sys.path.append('../StatsUFC/model')

import json

from BaseParse import ParserConsult
from bs4 import BeautifulSoup

from TestHelper import gt_and_doc, ComparingDicts, ComparingLists

def test_GetListFromBlockquote():
    gt_codes, bq_doc = gt_and_doc('tests/Pages/Consultant/GroundTruthCodes.txt', 
                                  'tests/Pages/Consultant/TestBlockquote.txt')

    pc = ParserConsult()

    codes = pc.GetListFromBlockquote(bq_doc)

    assert all([item == gt_item for item, gt_item in zip(codes, gt_codes)])

def test_GetListHeadersCodes():
    gt_headers, doc = gt_and_doc('tests/Pages/Consultant/GroundTruthHeaders.txt', 
                                 'tests/Pages/Consultant/Headers.txt')
    pc = ParserConsult()
    headers = pc.GetListHeadersCodes(doc)

    assert all([item == gt_item for item, gt_item in zip(gt_headers, headers)])

def test_ExtractNestedLists():
    with open('tests/Pages/Consultant/NestedList.txt', 'r', encoding='utf-8') as f:
        doc = f.read()

    pc = ParserConsult()
    codes_tree = pc.ExtractNestedLists(doc)
    print(codes_tree)

def test_GetArticleParagraphs():
    gt_paragraphs, doc = gt_and_doc('tests/Pages/Consultant/GroundTruthArticle.txt', 
                                    'tests/Pages/Consultant/Article.txt')
    pc = ParserConsult()
    paragraphs = pc.GetArticleParagraphs(doc)

    assert all([item == gt_item for item, gt_item in zip(gt_paragraphs, paragraphs)])

def test_GetAllCodes():
    pl = ParserConsult()

    gt_info, doc = gt_and_doc('tests/Pages/Consultant/GroundTruth/GetAllPopularCodes.json',
                              'tests/Pages/Consultant/Docs/GetAllPopularCodes.html')
    gt_info = ' '.join(gt_info)
    gt_info = json.loads(gt_info)

    extracted_info = pl.GetAllPopularCodes(doc)
    assert all(ComparingLists(gt_info.keys(), extracted_info.keys()))

def test_GetArticleName():
    pl = ParserConsult()

    gt_info, doc = gt_and_doc('tests/Pages/Consultant/GroundTruth/GetArticleName.json',
                              'tests/Pages/Consultant/Docs/GetArticleName.html')
    gt_info = ' '.join(gt_info)
    gt_info = json.loads(gt_info)

    extracted_info = pl.GetArticleName(doc)
    assert extracted_info == gt_info[0]

def test_GetArticleAndName():
    pl = ParserConsult()

    gt_info, doc = gt_and_doc('tests/Pages/Consultant/GroundTruth/GetArticleAndName.json',
                              'tests/Pages/Consultant/Docs/GetArticleAndName.html')
    gt_info = ' '.join(gt_info)
    gt_info = json.loads(gt_info)

    extracted_info = pl.GetArticleAndName(doc)
    assert extracted_info['Name'] == gt_info[0]



if __name__ == '__main__':
    test_GetListFromBlockquote()
    test_GetListHeadersCodes()
    test_ExtractNestedLists()
    test_GetArticleParagraphs()
    test_GetAllCodes()
    test_GetArticleName()
    test_GetArticleAndName()
