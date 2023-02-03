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
    
    def ExtractHeadersContent(self, doc, htype:int = 1):
        if isinstance(doc, str):
            doc = BeautifulSoup(doc, features = 'html.parser')
        tag = 'h' +  str(htype)
        headers = doc.find_all(tag)
        headers_content = [h.text.strip() for h in headers]
        return headers_content
    
    def ExtractNestedLists(self, doc, tag_list = 'ul', tag_leaf = 'li'):
        if isinstance(doc, str):
            doc = BeautifulSoup(doc, features = 'html.parser')
            doc = doc.contents[0]

        chapter = None
        nested_list = dict()
        for child in doc.contents:
            if child.name == tag_list:
                if child.find(tag_list):
                    nested_list[chapter] = self.ExtractNestedLists(child)
                else:
                    all_tags = child.find_all(tag_leaf)
                    #We can change below line for extract all inner text and only text, withou tags
                    #but for quickly realization in this place is contained simple realization
                    all_items = [item.text.strip() for item in all_tags]
                    nested_list[chapter] = all_items
            elif child.name == 'li':
                chapter = child.text
        
        return nested_list
    
        

        

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
        tournaments = []

        bst = BeautifulSoup(doc, features = 'lxml')

        table_stats = bst.find(attrs={'class': 'b-statistics__table-events'})
        tbody = table_stats.find('tbody')
        tournament_rows = tbody.find_all('tr')


        for t_row in tournament_rows:
            column1 = t_row.find('i') # contain name and  date
            information = dict.fromkeys(['name', 'date', 'type', 'city', 'country', 'state'])
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
                
                information['name'] = name
                information['date'] = f'{year}.{month}.{day}'#datetime.date(int(year), month, int(day)))
                information['country'] = country
                information['state'] = state
                information['city'] = city
                information['type'] = ParserUFCStats.ExtractTournamentType(name)
            tournaments.append(information)
        return tournaments

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
        4. total_stats_per_round;
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

        information['tournament'] = doc.find(attrs={'class': 'b-content__title'}).findChild().text.strip()
        
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
        bonuses = {fighter_1: [], fighter_2: []}
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
        
        if fight_type not in information:
            information[fight_type]='normal'

        if information[fight_type]=='belt':
            division = division.split(' ')
            if 'Ultimate' in division:
                division = division[3:]
                division.remove('Tournament')
            if 'Interim' in division:
                division = division[2:]
            division.remove('Title')
            division.remove('Bout')
        else:
            division = division.split(' ')
            division.remove('Bout')

        information['division'] = ' '.join(division) 

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
            try:
                controls_f1 = list(map(int, controls_str[0].split(':')))
            except:
                controls_f1 = [0,0]
            try:
                controls_f2 = list(map(int, controls_str[1].split(':')))
            except:
                controls_f2 = [0,0]
            return  [controls_f1[0]*60+ controls_f1[1], controls_f2[0]*60 + controls_f2[1]]



class ParserConsult(Parser):

    def __init__(self) -> None:
        super().__init__()

    '''
    Doc should contain list of paragraphs <p> in which containing <a>

    Return:
        list of texts
    '''
    def GetListFromBlockquote(self, doc):
        if isinstance(doc, str):
            doc = BeautifulSoup(doc, features='html.parser')

        list_links = doc.find_all('a')
        list_text = [a.text.strip() for a in list_links]
        return list_text
    
    '''
    Function for extract list of type popular codes on page:
    https://www.consultant.ru/popular/

    Args:
        doc:BeautifulSoup - document with content from above url
    Return:
        list[str] with codes types
    '''
    def GetListHeadersCodes(self, doc):
        return self.ExtractHeadersContent(doc, htype = 3)
    
    '''
    Function for extract types and corresponding popular codes from page:
    https://www.consultant.ru/popular/

    Args:
        doc:BeautifulSoup or str - document with content from above url
    Return:
        dict[list] with keys:
            1. Codes type
        Each codes type contain list of corresponding codes
    '''
    def GetAllPopularCodes(self, doc) -> dict[list]:
        if isinstance(doc, str):
            doc = BeautifulSoup(doc, features='html.parser')
        headers = self.GetListHeadersCodes(doc)
        div_content = doc.find(attrs = {'id': 'content'})
        blocks_codes = div_content.find_all('blockquote')

        codes = dict()
        for block_codes, header in zip(blocks_codes, headers):
            codes[header] = self.GetListFromBlockquote(block_codes)
        
        return codes
    
    '''
    Extract codes tree's.
    For example from page:
    https://www.consultant.ru/document/cons_doc_LAW_37800/
    Args:
        doc:BeautifulSoup or str - document with content from above url
    Return:
        dict graph with all codes tree
        on end of tree graph is contained list of article names
    '''
    def GetCodesTree(self, doc):
        if isinstance(doc, str):
            doc = BeautifulSoup(doc, features='html.parser')
        div_list = doc.find(attrs = {'class': 'document-page__toc'})
        nested_list = div_list.find('ul')
        codes_tree = self.ExtractNestedLists(nested_list)
        return codes_tree


    '''
    Finding article paragraphs in on special dict on page with articles.
    For example from page:
    https://www.consultant.ru/document/cons_doc_LAW_37800/d4ab16b974a8e08c3e3297ffcd28d0ac4ff111bb/

    Args:
        doc:BeautifulSoup or str - div with paragraphs 
        (for my use especially contained "class document-page__content document-page_left-padding")
    Return:
        list[str] with paragraphs for article
    '''
    def GetArticleParagraphs(self, doc):
        if isinstance(doc, str):
            doc = BeautifulSoup(doc, features='html.parser').contents[0]
        
        childs = doc.contents
        paragraphs = []
        for child in childs:
            if child.name == 'p' and child.contents:
                paragraphs.append(child.text.strip())

        return paragraphs
    
    '''
    Function for extract name of article from article page.
    For example: 
    https://www.consultant.ru/document/cons_doc_LAW_37800/d4ab16b974a8e08c3e3297ffcd28d0ac4ff111bb/

    Args:
        doc:BeautifulSoup or str - document with content from above url
    Return:
        Part of name with started withou name of codes. (Start from "Статья")
    '''
    def GetArticleName(self, doc):
        if isinstance(doc, str):
            doc = BeautifulSoup(doc, features = 'html.parser')
        div_head = doc.find(attrs = {'class': 'document__style doc-style'})
        par_name = div_head.find('p')
        article_name = par_name.text.strip()
        part_of_name = re.search('Статья *\d*(\.\d|) *([а-яА-Я]|\w|,|\"|,|\'|\.| )*', article_name)
        if part_of_name:
            part_of_name.group().strip()
        else:
            part_of_name = "Возможно, утратил силу" # из наблюдений
        return part_of_name
    
    '''
    Function for extract paragraphs of article and the name.
    For example from page:
    https://www.consultant.ru/document/cons_doc_LAW_37800/d4ab16b974a8e08c3e3297ffcd28d0ac4ff111bb/

    Args:
        doc:BeautifulSoup or str - document with content from above url
    Return:
        dict with keys:
            1. Name - str with name
            2. Paragraphs - list of strings with parts 
    '''
    def GetArticleAndName(self, doc):
        if isinstance(doc, str):
            doc = BeautifulSoup(doc, features = 'html.parser')
        
        output_info = dict()

        div_with_p = doc.find(attrs = {'class': 'document-page__content document-page_left-padding'})
        paragraphs = self.GetArticleParagraphs(div_with_p)
        article_name = self.GetArticleName(doc)
        
        output_info['Name'] = article_name
        output_info['Paragraphs'] = paragraphs
        return output_info


class ParserYuristOnline(Parser):

    def __init__(self) -> None:
        super().__init__()
    
    '''
    Extracting information from short block with question. It information contain:
        1. Name - str;
        2. City - str;
        3. Answers - int;
        4. Categories - list;
        5. Title - str;
        6. Datetime - str;
        7. Id - int.
    Args:
        doc - str or BeautifulSoup object which equal information block
    Return:
        Map with keys which are descripted above
    '''
    def GetShortQuestionBlock(self, doc):
        if isinstance(doc, str):
            doc = BeautifulSoup(doc, features='html.parser')
        
        output = dict()
        
        div_name = doc.find(attrs = {'class':'question-author'})
        output['Name'] = div_name.text.strip()

        div_datetime = doc.find(attrs = {'class': 'question-time'})
        date = div_datetime.contents[0].text.strip()
        time = div_datetime.contents[-1].text.strip()
        output['Datetime'] = date + " " + time

        div_title = doc.find(attrs = {'class': 'question-title'})
        output['Title'] = div_title.text.strip()

        div_cat_city = doc.find(attrs = {'class': 'question-category-city'})
        output['City'] = div_cat_city.contents[-1].text.strip()
        
        categories = []
        cat_tags = div_cat_city.find_all('a')
        for cat_tag in cat_tags:
            categories.append(cat_tag.text.strip())
        output['Categories'] = categories

        div_answers = doc.find(attrs = {'class': 'jurist-response-2'})
        text_answers = div_answers.text.strip()#problem https://www.yurist-online.net/question/p/394 - Томара, 29.06.2020
        output['Answers'] = int(re.search('\d{1,}', text_answers)[0])

        div_qdetails = doc.find(attrs = {'class': 'question-details'})
        attr_id = div_qdetails.get_attribute_list('id')
        id = None
        if attr_id:
            dirty_id = attr_id[0]
            id = int(dirty_id[1:])
        output['Id'] = id        

        return output

    '''
    Extract information from particular answer on particular question.
    For example from page:
    https://www.yurist-online.net/question/176758

    Args:
        doc:BeautifulSoup or str - particular answer.
    Return:
        dict with keys:
            1. Rating;
            2. Name;
            3. Text;
            4. Datetime.
    '''
    def GetAnswerInformation(self, doc):
        if isinstance(doc, str):
            doc = BeautifulSoup(doc, features='html.parser')
        output = dict()

        spans_star = doc.find_all(attrs = {'class': 'rating-star star-green'})
        output['Rating'] = len(spans_star) if spans_star else 0

        span_name = doc.find(attrs = {'itemprop': 'name'})
        output['Name'] = span_name.text.strip()

        div_text = doc.find(attrs = {'class':'answer-text'})
        text = div_text.get_text(separator=' ').strip()
        output['Text'] = text.replace("\n", "")

        time_text = doc.find('time').text.strip()
        time_text = time_text.split(' ')
        output['Datetime'] = time_text[0] + ' ' + time_text[-1]

        return output

    '''
    Extract all information from list with question.
    For example, from page:
        https://www.yurist-online.net/
    Args:
        doc:BeautifulSoup or str - document with content from above url
    Return:
        list[dict] with all short question (See function GetShortQuestionBlock)
    '''
    def GetAllShortQuestions(self, doc):
        if isinstance(doc, str):
            doc = BeautifulSoup(doc, features='html.parser')
        
        main_block = doc.find(attrs = {'class': 'main-block'})
        divs_question = main_block.find_all(attrs = {'class': 'white-block'})

        output = []
        for div_q in divs_question:
            output.append(self.GetShortQuestionBlock(div_q))
        
        return output

    '''
    Extract all information from list with question.
    For example, from page:
    https://www.yurist-online.net/question/176758
    
    Args:
        doc:BeautifulSoup or str - document with content from above url
    Return:
        list[dict] with all answers on question (See function GetAnswerInformation)
    '''
    def GetAllAnswers(self, doc):
        if isinstance(doc, str):
            doc = BeautifulSoup(doc, features='html.parser')
        
        divs_answers = doc.find_all(attrs = {'class': 'answer-block'})

        answers = []
        for div_answer in divs_answers:
            answers.append(self.GetAnswerInformation(div_answer))
        return answers 

    '''
    Extract text of question from page with question:
    Page  example:
    https://www.yurist-online.net/question/176642

    Full text question at the moment contain in div with class, which equal "question-details"
    Args:
        doc:BeautifulSoup or str - document with content from above url
    Return:
        str with full text of question
    '''
    def GetQuestionText(self, doc):
        if isinstance(doc, str):
            doc = BeautifulSoup(doc, features='html.parser')
        div_question = doc.find(attrs={'class':  'question-details'})
        question = div_question.text.strip()
        return question

    '''
    Extract question and answers from question page
    Page example:
    https://www.yurist-online.net/question/176642

    Args:
        doc:BeautifulSoup or str - document with content from above url
    Return:
        tuple(str, list[dict]).
        1. About str see description GetQuestionText
        2. About list[dict] see description GetAllAnswers
    '''
    def GetQuestAndAnswers(self, doc):
        question = self.GetQuestionText(doc)
        answers = self.GetAllAnswers(doc)
        return question, answers


