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
    
    For their version  '\n' is interpreted like separator if paragraphs and
    sep are put on place which contain one or more symbols '\n'
    '''
    def ExtractTBody(self, tbody, sep: str = ';', row_tag = 'tr', colum_tag = 'td'):
        if isinstance(tbody, str):
            tbody = BeautifulSoup(tbody, features = 'lxml')

        all_rows = tbody.find_all(row_tag)

        ex_rows = []
        
        for row in all_rows:
            ex_columns = []
            all_columns = row.find_all(colum_tag)
            for column in all_columns:
                column_text = []
                for elem in column.children:
                    inner_text = elem.get_text().strip()
                    if len(inner_text) > 0:
                        column_text.append(inner_text)
                column_text = sep.join(column_text)
                ex_columns.append(column_text)
            ex_rows.append(ex_columns)
        
        return ex_rows

    def ExtractTable(self, table, sep: str = ';'):
        if isinstance(table, str):
            table = BeautifulSoup(table, features = 'lxml')
        
        thead = table.find('thead')
        tbody = table.find('tbody')

        columns_name = self.ExtractTBody(thead, sep, row_tag = 'tr', colum_tag='th')[0]
        rows_features = self.ExtractTBody(tbody)

        table = {column: [] for column in columns_name}
        rows_features = [[rows_features[j][i] for j in range(len(rows_features))] for i in range(len(rows_features[0]))]
        for i, column in enumerate(columns_name):
            table[column] = rows_features[i]

        return table



        



class ParserUFCStats(Parser):

    def __init__(self) -> None:
        month_names = list(filter(lambda x: len(x) > 0, calendar.month_name))
        self.map_month_names = {month_names[i]: i + 1 for i in range(12)}

        self.keys_total_stats = ['knockdown', 'sig_strikes', 'sig_strikes_total', 
                                 'total_strikes', 'all_total_str', 
                                 'takedown', 'takedown_total' ,'sub_att', 'rev', 'ctrl']
        extr_total_stats = ['Fighter', 'KD', 'Sig. str.', 'Sig. str. %', 'Total str.', 'Td',
                             'Td %', 'Sub. att', 'Rev.', 'Ctrl']
        
        self.map_extr_several_total = {'Sig. str.': ('sig_strikes', 'sig_strikes_total'),
                                       'Total str.': ('total_strikes', 'all_total_str'),
                                       'Td': ('takedown', 'takedown_total')}
        

    
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
        table - is table with stats
    '''
    def GetTotalStats(self, table:str):
        if isinstance(table, str):
            table = BeautifulSoup(table, features='lxml')
        extr_table = {k: elem[0] for k, elem in self.ExtractTable(table).items()}

        information = dict.fromkeys(self.keys_total_stats)

        #'Fighter', 'KD', 'Sig. str.', 'Sig. str. %', 'Total str.', 'Td',
        #'Td %', 'Sub. att', 'Rev.', 'Ctrl'

        #'knockdown', 'sig_strikes', 'sig_strikes_total', 
        #'total_strikes', 'all_total_str',
        #'takedown', 'takedown_total' ,'sub_att', 'rev', 'ctrl'
        information['knockdown'] = list(map(int, extr_table['KD'].split(';')))
        information['rev'] = list(map(int, extr_table['Rev.'].split(';')))
        controls_str = extr_table['Ctrl'].split(';')
        controls_f1 = list(map(int, controls_str[0].split(':')))
        controls_f2 = list(map(int, controls_str[1].split(':')))
        information['ctrl'] = [controls_f1[0]*60+ controls_f1[1], controls_f2[0]*60 + controls_f2[1]]

        for key in self.map_extr_several_total.keys():
            feature_1, feature_2 = self.__split_stats_halper(extr_table[key])
            clear_features = self.map_extr_several_total[key]
            information[clear_features[0]] = feature_1
            information[clear_features[1]] = feature_2


        #'Israel Adesanya;Alex Pereira', '0;0', '86 of 162;91 of 157', '53%;57%', 
        # '119 of 209;140 of 214', '1 of 4;1 of 1', '25%;100%', '0;0', '0;0', '6:34;0:31'
        return information 

    '''
    Because exist lines like 'a1 of b1;a2 of b2', we should to split it line to
    two arrays: [a1, a2], [b1, b2]. For totals stats not want write similar code for it

    Args:
        line - str, which should contain structure 'a1 of b1;a2 of b2';
        n_between - str, which split blocks with a1, b1 and a2, b2;
        f_between - str, which split numbers a1 and b1, a2 and b2.
    Return:
        Two arrays which have structure: [a1, b1], [a2, b2]
    '''
    def __split_stats_halper(self, line:str, n_between = 'of', f_between = ';'):
        stats_sc = line.split(f_between) #  str 'Sig. str.' equal 'n1 of n2; n3 of n4'
        stats_bsc_1 = list(map(int, stats_sc[0].split(n_between))) # sig_str_by_fighter[0] element equal 'n1 of n2'
        stats_bsc_2 = list(map(int, stats_sc[1].split(n_between))) # sig_str_by_fighter[1] element equal 'n3 of n4'
        feature_1 = [stats_bsc_1[0], stats_bsc_2[0]]
        feature_2 = [stats_bsc_1[1], stats_bsc_2[1]]
        return feature_1, feature_2

        
        

