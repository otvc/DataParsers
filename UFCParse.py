from bs4 import BeautifulSoup
import re
import calendar
import datetime 
import copy

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

    '''
    Function, which extracted information from html table.
    Html table should have tags: thead, tbody.
    From thead extracted features of table, and values from each feature are extracted
    from tbody.
        Args:
            table - is particular table, form which we want to extract data
            sep - separator paragraphs (uses if in <td><\td> contain several paragraphs)
        Return:
            map - where each key equal to column name from thead
            and value corresponding particular key is list of values from tbody in str type
    '''
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
        

    '''
    Auxiliary function for extract type of tournament.
        Args:
            str - string, from which type of tournament is wanted to extract
        Return:
            Tournament type. Where nt mean Normal Tournament and FN mean Fight Night
    '''    
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
        4. total_stats_per_round
        5. division;
        6. round;
        7. seconds;
        8. bonuses;
        9. round_stats - each fight contain information like total_stats but per round. For each fight it's array of map like total_stats;
        10. sign_strikes - :
            10.1. head;
            10.2. head_total;
            10.3. body;
            10.4. body_total;
            10.5. leg;
            10.6. leg_total;
            10.7. distance;
            10.8. distance_total;
            10.9. clinch;
            10.10. clinch_total;
            10.11. ground;
            10.12. ground_total.
        11. sign_stats_per_round - same like round_stats but contain sig_strikes per round
        12. nicknames;
        13. type;
        14. method;
        15. time_format;
        16. referee;
        17. details.
    '''
    def GetFightStats(self, doc):
        if isinstance(doc, str):
            doc = BeautifulSoup(doc, features='html.parser')
        information = dict()
        
        fighters_top_line = doc.find(attrs={'class':'b-fight-details__persons clearfix'})
        a_fighters_names = fighters_top_line.find_all(attrs={'class':'b-link b-fight-details__person-link'})
        fighter_1 = a_fighters_names[0].text.strip()
        fighter_2 = a_fighters_names[1].text.strip()
        information['fighters'] = [fighter_1, fighter_2]

        a_nicknames = fighters_top_line.find_all(attrs = {'class': 'b-fight-details__person-title'})
        nickname_1 = a_nicknames[0].text.strip()[1:-1]
        nickname_2 = a_nicknames[1].text.strip()[1:-1]
        information['nicknames'] = [nickname_1, nickname_2]

        fight_results = fighters_top_line.find_all(attrs = {'class': 'b-fight-details__person-status'})
        result_1 = fight_results[0].text.strip()
        result_2 = fight_results[1].text.strip()
        winner = 'winner'
        information[winner] = 'without'
        if result_1 == 'W':
            information[winner] = fighter_1
        elif result_2 == 'W':
            information[winner] = fighter_2
        
        division_i = doc.find(attrs = {'class':'b-fight-details__fight-title'})
        images = division_i.find_all('img')
        fight_type = 'type'
        if images:
            bonuses = {fighter_1: [], fighter_2: []}
            images.__iter__()
            for image in images:
                src = image['src']
                result = re.search('\w*.png', src)[0]
                if result:
                    result = result[:-4]
                    if result == 'belt':
                        information[fight_type] = result
                    elif result == 'fight':
                        bonuses[fighter_1].append(result)
                        bonuses[fighter_2].append(result)
                    elif information[winner] != 'without':
                        bonuses[information[winner]].append(result)
        else:
            information[fight_type] = 'normal'
        information['bonuses'] = bonuses
        
        division = list(division_i.children)[-1].strip()
        division = division.split(' ')[1]
        information['division'] = division 

        short_stats_line = doc.find(attrs={'class':'b-fight-details__content'})
        
        first_ssl_paragraph = short_stats_line.find_all(attrs={'class':'b-fight-details__text'})[0]
        items_ssl_i = first_ssl_paragraph.find_all(attrs = {'class': 'b-fight-details__label'})
        information['method'] = short_stats_line.find(attrs={'style':'font-style: normal'}).text.strip()
        
        round = items_ssl_i[1].next_sibling.strip()
        round = int(round)
        information['round'] = int(round)

        times = items_ssl_i[2].next_sibling.strip()
        minutes, seconds = list(map(int, times.split(':')))
        information['seconds'] =  round*60*60+minutes*60+seconds

        time_format = items_ssl_i[3].next_sibling.text.strip()
        information['time_format'] = int(time_format[0])

        referee = items_ssl_i[4].next_sibling.next_sibling.text.strip()
        information['referee'] = referee

        second_ssl_paragraph = short_stats_line.find_all(attrs={'class':'b-fight-details__text'})[1]
        information['Details'] = list(second_ssl_paragraph.children)[-1].text.strip()

        stats_sections = doc.find_all(attrs={'class': 'b-fight-details__section'})
        total_stats_table = stats_sections[1].find('table')
        thead_total_stats = total_stats_table.find('thead')
        information['total_stats'] = self.GetTotalStats(total_stats_table)
        sign_stats_table = stats_sections[3].next_sibling.next_sibling
        thead_sign_stats = sign_stats_table.find('thead')
        information['sign_strikes'] = self.GetSignificantStats(sign_stats_table)

        tables = doc.find_all(attrs={'class': 'b-fight-details__table js-fight-table'})
        information['total_stats_per_round'] = self.GetTotalStatsPerRound(tables[0], thead_total_stats)
        information['sign_stats_per_round'] = self.GetSignificantStatsPerRound(tables[1], thead_sign_stats)
        
        return information


    '''
    Auxiliary function for function GetFightStats.
    GetTotalStats help extract total_stats (look in description of function GetFightStats) 
    Args:
        table - is table with stats
    '''
    def GetTotalStats(self, table:str):
        if isinstance(table, str):
            table = BeautifulSoup(table, features='html.parser')
        extr_table = {k: elem[0] for k, elem in self.ExtractTable(table).items()}

        information = dict.fromkeys(self.keys_total_stats)

        self.ConvertStatsFromTable(information, extr_table, {'KD': 'knockdown', 'Rev.': 'rev'}, 
                                   self.map_extr_several_total, {'Ctrl': 'ctrl'}, {'Ctrl': self.__convert_ctrl})

        return information
    
    '''
    Function, for extraction stats from table with significant strikes stats
    '''
    def GetSignificantStats(self, table:str):
        if isinstance(table, str):
            table = BeautifulSoup(table, features='lxml')
        extr_table = {k: elem[0] for k, elem in self.ExtractTable(table).items()}
        
        need_extr_f = ['Head', 'Body', 'Leg', 'Distance', 'Clinch', 'Ground']
        map_extr_several = {feature: (feature.lower(), feature.lower()+'_total') for feature in need_extr_f}

        information = dict()

        self.ConvertStatsFromTable(information, extr_table, map_to_several=map_extr_several)

        return information
    
    '''
    Auxiliary function for converting extracted information from html table 
    and convert in correct format for us.
    Args:
        information - dictionary, into which information are collected from ext_table 
        ext_talbe - dictionary, which corresponding table
        map_to_feature - dictionary, which convert name of feature from ext_table to another name in information dictionary
        map_to_several - dictionary, which convert name of feature from ext_table to anothers 2 features in information
        and split particular value from ext_table by symbol ';' (it should be fix)
        map_to_tf - same like map_to_feature, but for column with times
        map_to_tf_call - dictionary, which contain function by key, in order transform time in str to time in necessary format
        each key is corresponding key in map_to_tf
    Return:
        None, but change information dictionary 
    '''
    def ConvertStatsFromTable(self,
                              information: dict,
                              extr_table: dict, 
                              map_to_feature: dict[str, str] = {}, 
                              map_to_several: dict[str, tuple[str, str]] = {},
                              map_to_tf: dict = {},
                              map_to_tf_call: dict = {}):

        for key in map_to_feature.keys():
            information[map_to_feature[key]] = list(map(int, extr_table[key].split(';')))

        for key in map_to_tf.keys():
            information[map_to_tf[key]] = map_to_tf_call[key](extr_table[key]) 

        for key in map_to_several.keys():
            feature_1, feature_2 = self.__split_stats_halper(extr_table[key])
            clear_features = map_to_several[key]
            information[clear_features[0]] = feature_1
            information[clear_features[1]] = feature_2

    def GetTotalStatsPerRound(self, table, thead):
        stats_per_round = self.GetStatsPerRound(table, thead, self.GetTotalStats)
        return stats_per_round
    
    def GetSignificantStatsPerRound(self, table, thead):
        stats_per_round = self.GetStatsPerRound(table, thead, self.GetSignificantStats)
        return stats_per_round
    

    '''
    Function, which is needed to extract information from rounds table.
    Args:
        table - is table, which containing tbodies with our stats, but for these tbodies aren't correctful
        thead in table.
        thead - thread, which contain columns name for tbodies and solve problem with their absence in main table
        get_stats_from_tbody - function, which execute stats from tbody (GetTotalStats, GetSignificantStats)
    '''
    def GetStatsPerRound(self, table, thead, get_stats_from_tbody):
        if isinstance(table, str):
            table = BeautifulSoup(table, features='html.parser')
        if isinstance(thead, str):
            thead = BeautifulSoup(thead, features='html.parser')
        tbodies = table.find_all('tbody')
        tbodies_iter = tbodies.__iter__()
        next(tbodies_iter)
        stats_per_round = []
        for tbody in tbodies_iter:
            imagen_table = BeautifulSoup('<table></table>',  features='html.parser')
            imagen_table.table.append(copy.copy(thead))
            imagen_table.table.append(tbody)
            stats_round = get_stats_from_tbody(imagen_table)
            stats_per_round.append(stats_round)
        
        return stats_per_round

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

    def __convert_ctrl(self, ctrl_str: str):
            controls_str = ctrl_str.split(';')
            controls_f1 = list(map(int, controls_str[0].split(':')))
            controls_f2 = list(map(int, controls_str[1].split(':')))
            return  [controls_f1[0]*60+ controls_f1[1], controls_f2[0]*60 + controls_f2[1]]
