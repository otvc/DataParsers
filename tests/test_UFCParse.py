import sys
import os
import calendar

sys.path.append('../StatsUFC')

from BaseParse import ParserUFCStats
from BaseParse import Parser

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from datetime import date

from bs4 import BeautifulSoup


def test_GetTournaments():
    with open('tests/Pages/UFCStats/Stats _ UFC.html', 'r') as f:
        html = f.read()
    
    pufc = ParserUFCStats()
    
    gt_keys = ['name', 'date', 'type', 'city','country', 'state']
    gt_keys.sort()

    gt_values = ['UFC Fight Night: Thompson vs. Holland',
                 "2022.12.3",
                 'FN',
                 'Orlando',
                 'USA',
                 'Florida']

    information = pufc.GetTournaments(html)[1]
    keys = list(information.keys())
    keys.sort()
    
    assert len(keys) == len(gt_keys)
    assert all(a == b for a, b in zip(keys, gt_keys))

    extracted_values = [information['name'],
                    information['date'],
                    information['type'],
                    information['city'],
                    information['country'],
                    information['state']]

    
    #assert all(a == b for a, b in zip(gt_values, extracted_values))

    


def test_ExtractTournamentType():
    fn_str = 'UFC Fight Night: Thompson vs. Holland'
    nt_str = 'UFC 281: Adesanya vs. Pereira'

    fn_extracted = ParserUFCStats.ExtractTournamentType(fn_str)
    nt_extracted = ParserUFCStats.ExtractTournamentType(nt_str)

    assert fn_extracted == 'FN'
    assert nt_extracted == 'NT'

def test_GetTotalStats():
    with open('tests/Pages/UFCStats/TotalStats.html', 'r') as f:
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

def test_GetSignificantStats():
    with open('tests/Pages/UFCStats/SignificantStrike.html', 'r') as f:
        table = f.read()

    gt_keys = ['head', 'head_total', 'body', 'body_total', 
               'leg', 'leg_total', 'distance', 'distance_total',  
               'clinch', 'clinch_total', 'ground', 'ground_total']
    gt_keys.sort()
    gt_values = {
        'head': [41, 42], 'head_total': [103, 89], 
        'body': [21,  27], 'body_total': [29, 33], 
        'leg': [24, 22], 'leg_total': [30, 35], 
        'distance': [77, 76], 'distance_total': [148, 139],  
        'clinch': [3, 14], 'clinch_total': [4, 17], 
        'ground': [6, 1], 'ground_total': [10, 1]
    }

    pfc = ParserUFCStats()
    information = pfc.GetSignificantStats(table)

    ex_keys = list(information.keys())
    ex_keys.sort()

    assert len(ex_keys) == len(gt_keys)
    assert all(a == b for a, b in zip(ex_keys, gt_keys))
    assert all(a == b for a, b in zip(gt_values, information))

def test_GetTotalStatsPerRound():
    with open('tests/Pages/UFCStats/TotalStatsPerRound.html', 'r') as f:
        table = f.read()
    with open('tests/Pages/UFCStats/TotalStatsThead.html', 'r') as f:
        thead = f.read()
    pfc = ParserUFCStats()
    informations = pfc.GetTotalStatsPerRound(table, thead)
    ex_keys = list(informations[0].keys())

def test_GetFightStats():
    with open('tests/Pages/UFCStats/FightPage.html', 'r') as f:
        doc = f.read()
    
    pfc = ParserUFCStats()
    pfc.GetFightStats(doc)
    
    

def test_ExtractTBody():
    with open('tests/Pages/UFCStats/TBody.html') as f:
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
    with open('tests/Pages/UFCStats/TotalStats.html') as f:
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
    test_ExtractTournamentType()
    test_GetTournaments()
    
    test_ExtractTBody()
    test_ExtractTable()

    test_GetTotalStats()
    test_GetSignificantStats()
    test_GetTotalStatsPerRound()
    test_GetFightStats()


