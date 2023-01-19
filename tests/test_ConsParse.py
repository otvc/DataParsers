import sys
sys.path.append('../StatsUFC/model')

from BaseParse import ParserConsult
from bs4 import BeautifulSoup

def gt_and_doc(path_gt, path_doc, e1='utf-8', e2 = 'utf-8'):
    with open(path_gt,  'r', encoding=e1) as f:
        ground_truth = f.readlines()
        ground_truth = [line.strip() for line in ground_truth]

    with open(path_doc, 'r', encoding=e2) as f:
        doc = f.read()
    
    return ground_truth, doc

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

if __name__ == '__main__':
    test_GetListFromBlockquote()
    test_GetListHeadersCodes()
    test_ExtractNestedLists()
    test_GetArticleParagraphs()
