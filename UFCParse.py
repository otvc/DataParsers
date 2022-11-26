from bs4 import BeautifulSoup
import re
import calendar
import datetime 

class Parser:
    
    def __init__(self) -> None:
        pass

    '''
    Value extracted with strip
    Args:
        tbody - string each contain information abou tbody
        sep - if td of column contain more than one paragraph, therefore several 
              paragraph should be separated from each of them.
              Then sep - str symbol which each separate information from each other;
    Return:
        Matrix (list of lists), where value on row and columns equal
        text value on across row and column of tbody
    '''
    def ExtractTBody(self, tbody: str, sep: str = ';'):
        pass



class ParserUFCStats(Parser):

    def __init__(self) -> None:
        month_names = list(filter(lambda x: len(x) > 0, calendar.month_name))
        self.map_month_names = {month_names[i]: i + 1 for i in range(12)}

    
    def ExtractTournamentType(str):
        inf = re.search('UFC \d{3}', str)
        if inf:
            return 'NT'
        else:
            return 'FN'


    '''
    This function using for obtaining name of UFC tournament from uri (http://www.ufcstats.com/statistics/events/completed)
    with uri, which provide on page about tournament

    Args:
        doc - html str, which contain html data from recieve to http://www.ufcstats.com/statistics/events/completed
    Return:
        Map with information about the tournament. That is map contain keys:
            1. name;
            2. date;
            3. type;
            4. city;
            5. country;
            6. state;
        For each key connected list, which order are important, because value on index "i" 
        across all keys describe the tournament 
    '''
    def GetTournaments(self, doc:str):
        information = {
            'name': [],
            'date': [],
            'type': [],
            'city': [],
            'country': [],
            'state': []
        }

        bst = BeautifulSoup(doc, features = 'lxml')

        table_stats = bst.find(attrs={'class': 'b-statistics__table-events'})
        tbody = table_stats.find('tbody')
        tournament_rows = tbody.find_all('tr')

        for t_row in tournament_rows:
            column1 = t_row.find('i') # contain name and  date

            if column1:
                name_container = column1.find('a')
                date_container = column1.find('span')

                name = name_container.text.strip()
                
                date = date_container.text.strip()
                month, day, year = date.split(' ')
                day = day[:-1] # drop ',' after day
                month = self.map_month_names[month]

                column2 = t_row.find_all('td')[1]
                location = column2.text.split(',')
                location = [loc.strip() for loc in location]

                if len(location) == 3:
                    city, state, country = location
                else:
                    state = ''
                    city, country = location
                
                information['name'].append(name)
                information['date'].append(datetime.date(int(year), month, int(day)))
                information['country'].append(country)
                information['state'].append(state)
                information['city'].append(city)
                information['type'].append(ParserUFCStats.ExtractTournamentType(name))

        return information

    '''
    This function using to extract information from page something equal http://www.ufcstats.com/event-details/012fc7cd0779c09a
    
    Args:
        doc - html str, which contain html data from recieve to the page
    Return:
        return map with next features:
        1. fighters - each element of array is array with two fighters
        2. winner - Name of winner fight
        3. total_stats - each ellement of array is object with keys:
            3.1. knockdown - array of stats knockdowns by each fighters (index of element equal index of fighter in 1. point);
            3.2. sig_strikes;
            3.3. sig_strikes_total;
            3.4. total_strikes;
            3.5. all_total_str;
            3.6. takedown;
            3.7. takedown_total;
            3.8. sub_att;
            3.9. rev;
            3.10. ctrl;
        4. weight_class;
        5. round;
        6. seconds;
        7. bonus;
        8. round_stats - each fight contain information like total_stats but per round. For each fight it's array of map like total_stats;
        9. sig_strikes - :
            9.1. head;
            9.2. body;
            9.3. leg;
            9.4. distance;
            9.4. clinch;
            9.5. ground;
        10. sig_stats_per_round - same like round_stats but contain sig_strikes per round
    '''
    def GetFightStats(self, doc:str):
        pass
    
    '''
    Auxiliary function for function GetFightStats.
    GetTotalStats help extract total_stats (look in description of function GetFightStats) 
    Args:
        doc - is table with stats
    '''
    def GetTotalStats(self, doc:str):
        keys_info = ['knockdown', 'sig_strikes', 'sig_strikes_total', 
                     'total_strikes', 'all_total_str', 
                     'takedown', 'takedown_total' ,'sub_att', 'rev', 'ctrl']

        information = {key: [] for key in keys_info}

        table = BeautifulSoup(doc, features='lxml')

        return information
        

