import sys
sys.path.append('../StatsUFC/model')

from BaseParse import ParserYuristOnline
from test_ConsParse import gt_and_doc
import json

from bs4 import BeautifulSoup

def ComparingDicts(d1, d2, result = []):
    for key, value in d1.items():
        if isinstance(value, dict):
            ComparingDicts(value, d2[key], result)
        elif isinstance(value, list):
            list_equals = [i1 == i2  for i1, i2 in zip(value, d2[key])]
            result.extend(list_equals)
        elif isinstance(value, str):
            v1 = value.replace(" ", "")
            v2 = d2[key].replace(" ", "")
            result.append(v1 == v2)
        else:
            result.append(value == d2[key])
    return result

def ComparingLists(l1, l2, result = []):
    for i1, i2 in zip(l1, l2):
        if isinstance(i1, dict):
            ComparingDicts(i1, i2, result=result)
        elif isinstance(i1, list):
            ComparingLists(i1, i2, result=result)
        else:
            result.append(i1==i2)
    return result

        

def test_GetShortQuestionBlock():
    gt_info, doc = gt_and_doc('tests/Pages/yourist-online/GroundTruth/ShortQuestionBlock.json',
                              'tests/Pages/yourist-online/Docs/ShortQuestionBlock.html')
    gt_info = ' '.join(gt_info)
    gt_info = json.loads(gt_info)

    pl = ParserYuristOnline()
    extracted_info = pl.GetShortQuestionBlock(doc)

    assert all(ComparingDicts(gt_info, extracted_info))

def test_GetAnswerInformation():
    gt_info, doc = gt_and_doc('tests/Pages/yourist-online/GroundTruth/GetAnswerInformation.json',
                              'tests/Pages/yourist-online/Docs/GetAnswerInformation.html')
    gt_info = ' '.join(gt_info)
    gt_info = json.loads(gt_info)

    pl = ParserYuristOnline()
    extracted_info = pl.GetAnswerInformation(doc)

    assert all(ComparingDicts(gt_info, extracted_info))

def test_GetAllShortQuestions():
    gt_info, doc = gt_and_doc('tests/Pages/yourist-online/GroundTruth/GetAllShortQuestions.json',
                              'tests/Pages/yourist-online/Docs/GetAllShortQuestions.html', e2=None)
    gt_info = ' '.join(gt_info)
    gt_info = json.loads(gt_info)

    pl = ParserYuristOnline()
    extracted_info = pl.GetAllShortQuestions(doc)[:2]

    assert all(ComparingLists(gt_info, extracted_info))

def test_GetAllAnswers():
    pl = ParserYuristOnline()

    gt_info, doc = gt_and_doc('tests/Pages/yourist-online/GroundTruth/GetAllAnswers.json',
                              'tests/Pages/yourist-online/Docs/GetAllAnswers.html', e2=None)
    gt_info = ' '.join(gt_info)
    gt_info = json.loads(gt_info)

    extracted_info = pl.GetAllAnswers(doc)

    assert all(ComparingLists(gt_info, extracted_info))


if __name__ == '__main__':
    test_GetShortQuestionBlock()
    test_GetAnswerInformation()
    test_GetAllShortQuestions()
    test_GetAllAnswers()