import sys
sys.path.append('../StatsUFC/model')

from Stroller import BaseStoller

def test_plug(a, b):
    pass

def test_BaseStollerInit():
    fight_page_graph = {
        'http://www.ufcstats.com/event-details':
            {
                'http://www.ufcstats.com/fight-details/': None
            },
        'http://www.ufcstats.com/statistics/events/completed?page=': None
    }
    fight_page_graph['http://www.ufcstats.com/statistics/events/completed?page='] = fight_page_graph
    
    transition_graph = {'http://www.ufcstats.com/statistics/events/completed': fight_page_graph}

    particular_attr = ['href', 'data-link']

    bs = BaseStoller(transition_graph, particular_attr, test_plug)
    bs.StartWandering()


if __name__  == '__main__':
    test_BaseStollerInit()