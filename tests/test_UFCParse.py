import sys
import os
import calendar

sys.path.append('../StatsUFC')

from UFCParse import ParserUFCStats
from UFCParse import Parser

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from datetime import date


def test_GetTournaments():
    with open('tests/Pages/Stats _ UFC.html', 'r') as f:
        html = f.read()
    
    pufc = ParserUFCStats()
    
    gt_keys = ['name', 'date', 'type', 'city','country', 'state']
    gt_keys.sort()

    gt_values = ['UFC Fight Night: Thompson vs. Holland',
                 date(2022, 12, 3),
                 'FN',
                 'Orlando',
                 'USA',
                 'Florida']

    information = pufc.GetTournaments(html)
    keys = list(information.keys())
    keys.sort()
    
    assert len(keys) == len(gt_keys)
    assert all(a == b for a, b in zip(keys, gt_keys))

    extracted_values = [information['name'][0],
                    information['date'][0],
                    information['type'][0],
                    information['city'][0],
                    information['country'][0],
                    information['state'][0]]

    
    assert all(a == b for a, b in zip(gt_values, extracted_values))

    


def test_ExtractTournamentType():
    fn_str = 'UFC Fight Night: Thompson vs. Holland'
    nt_str = 'UFC 281: Adesanya vs. Pereira'

    fn_extracted = ParserUFCStats.ExtractTournamentType(fn_str)
    nt_extracted = ParserUFCStats.ExtractTournamentType(nt_str)

    assert fn_extracted == 'FN'
    assert nt_extracted == 'NT'

def test_GetTotalStats():
    with open('tests/Pages/TotalStats.html', 'r') as f:
        table = f.read()

    gt_keys = ['knockdown', 'sig_strikes', 'sig_strikes_total', 
               'total_strikes', 'all_total_str', 
               'takedown', 'takedown_total' ,'sub_att', 'rev', 'ctrl']
    gt_keys.sort()
    gt_values = {
        'knockdown': [0, 0],
        'sig_strikes': [86, 91],
        'sig_strikes_total': [162, 157],
        'total_strikes': [119, 140],
        'all_total_str': [209, 214],
        'takedown': [1, 1],
        'takedown_total': [4, 1],
        'sub_att': [0, 0],
        'rev': [0, 0],
        'ctrl': [6*60+34, 31]
    }

    pfc = ParserUFCStats()
    information = pfc.GetTotalStats(table)

    ex_keys = list(information.keys())
    ex_keys.sort()

    assert len(ex_keys) == len(gt_keys)
    assert all(a == b for a, b in zip(ex_keys, gt_keys))
    assert all(a == b for a, b in zip(gt_values, information))


def test_ExtractTBody():
    with open('tests/Pages/TBody.html') as f:
        tbody = f.read()

    gt_tb = [['Israel Adesanya;Alex Pereira', '0;0', '86 of 162;91 of 157', '53%;57%', 
              '119 of 209;140 of 214', '1 of 4;1 of 1', '25%;100%', '0;0', '0;0', '6:34;0:31']]
    gt_row = gt_tb[0]

    p = Parser()
    extracted_tb = p.ExtractTBody(tbody)
    extracted_row = extracted_tb[0]

    assert len(gt_row) == len(extracted_row)
    assert all(a == b for a,b in zip(extracted_row, gt_row))

def test_ExtractTable():
    with open('tests/Pages/TotalStats.html') as f:
        tbody = f.read()
    
    gt_th = [['Fighter', 'KD', 'Sig. str.', 'Sig. str. %', 'Total str.', 'Td',
               'Td %', 'Sub. att', 'Rev.', 'Ctrl']][0]

    gt_tb = [['Israel Adesanya;Alex Pereira', '0;0', '86 of 162;91 of 157', '53%;57%', 
              '119 of 209;140 of 214', '1 of 4;1 of 1', '25%;100%', '0;0', '0;0', '6:34;0:31']]
    gt_row = gt_tb[0]

    p = Parser()
    extracted_table = p.ExtractTable(tbody)
    extracted_values = extracted_table.values()
    extracted_keys = list(extracted_table.keys())
    extracted_tb = [column[0] for column in extracted_values]

    assert len(gt_th) == len(extracted_keys)
    assert all(a == b for a,b in zip(extracted_tb, gt_row))


    

    

if __name__ == '__main__':
    a = [[1, 2, 3], [4, 5, 6]]
    print(a[0][:])
    test_ExtractTournamentType()
    test_GetTournaments()
    
    test_ExtractTBody()
    test_ExtractTable()

    test_GetTotalStats()


