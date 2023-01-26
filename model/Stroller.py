import re

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions

from collections.abc import Callable
from bs4 import BeautifulSoup

class BaseFilter:
    '''
    This class needed to filtrate clickabble elements.
    In first step he filter element's by text which should satisfaction regular expression
    '''
    def __init__(self, regex_texts:list[str] = None) -> None:
        self.regex_texts = regex_texts
    
    def Filtration(self, elements):
        if self.regex_texts:
            elements = self.FiltrationTextsByRegex(elements)
        return elements
    
    def FiltrationTextsByRegex(self, elements:list[BeautifulSoup]) -> list[BeautifulSoup]:
        filtered = elements
        if self.regex_texts:
            for regex_text in self.regex_texts:
                filtered = self.FilterByInnerText(filtered, regex_text)
        return filtered
    
    def FilterByInnerText(self, elements:list[BeautifulSoup], regex) -> list[BeautifulSoup]:
        output = list(filter(lambda x: re.match(regex, x.text.strip()), elements))
        return output

class BaseStoller:
    '''
    
    Args:
        transition_graph:dict - it's graph which contain url for transition from page1 to page2
        when exist possobility for this transition on page1.
        transition_graph don't need to contain particulary url. keys should contain base part of source.
        Transition on next page happens if part uri contain this base part of source.
        particular_attr:list[str] - contain attributes in which will searching sources from transition_graph
        page_processed: Callable[[str, str]] - callable function, where arguments are equal:
            1.URI
            2.HTML document 
        inner_text_filter: Union[re,str] -  expression for filtration clickable elements by inner text
            if inner text contain pattern, that element is fits
        filters:dict[BaseFilter] - contain filters by base url (url is needed contain in "transition_graph")
                                   and drop clickable object, which have found and which not satifaction to filter
    '''
    def __init__(self, transition_graph:dict,
                       particular_attr:list[str],
                       page_processed: Callable[[str, str]] = lambda x,y: x,
                       filters:dict[BaseFilter]= None) -> None:
        self.transition_graph = transition_graph
        self.page_processed = page_processed
        self.particular_attr = particular_attr
        self.filters = filters
        self.set_options()
        self.set_driver()

        self.history = [] #contain pages which is viewed

    '''
    Function which create option for setting up webdriver
    '''
    def set_options(self):
        self.options = Options()
        self.options.headless = True
        self.options.add_argument('--window-size=1920,1080')
        self.options.add_argument('start-maximized')

        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_experimental_option(
            "prefs", {"profile.managed_default_content_settings.images": 2}
        )

    def set_driver(self):
        self.driver = webdriver.Chrome()

    '''
    Function which start wandering
        Args:
            transition graphs - same as in __init__
        Return:
            None
    '''
    def StartWandering(self, transition_graph = None):
        if not transition_graph:
            transition_graph = self.transition_graph
        self.Step(transition_graph)
    
    '''
    Function which contain next parts, which is needed for wandering:
    1. Goes on vertexes 1-st depth from transition_graph
    2. Finding on particular page sources which correspond to values for 1-st depth vertex
    in graph
    3. And goes to the next depth if contain needed sources
    Something like deep crawl
        Args:
            transition_graph - same function as in __init__
            page_is_loaded - it's needed if you return on page where you were
            and don't do request
        Return:
            None
    '''
    def Step(self, transition_graph, page_is_loaded = False):
        for current_page, next_transition in transition_graph.items():
            self.history.append(current_page)
            if not page_is_loaded:
                self.driver.get(current_page)
            self.page_processed(self.driver.current_url, self.driver.page_source)
            if next_transition: # if next page is not none. If page is None that it's mean stop 
                base_sources = list(next_transition.keys())
                elems_nodes = self.FindClickableElements(self.driver.page_source, base_sources) # if clickable elements didn't exist
                elems_nodes = self.Filtration(elems_nodes, base_sources[0]) #filtering elements
                elems_xpaths = self.ConvertNodesToXpaths(elems_nodes)
                #then recursion end.
                #If we seen source (contained in history)
                for node_xpath in elems_xpaths:
                    pl_elements = WebDriverWait(self.driver, 5, self.driver.find_element_by_xpath(node_xpath)).until(
                                expected_conditions.presence_of_element_located((By.XPATH, node_xpath))
                    )
                    self.StepClick(pl_elements, next_transition)

    '''
    Function which execute click for elements with source in order switch webdriver on this uri
    and get html page. In the next step transition.
        Args:
            element - clickable element for next step in site graph
            transition_graph - same function as writed in __init__
        Return:
            None
    '''
    def StepClick(self, element, transition_graph):
        element.click()
        self.Step(transition_graph, page_is_loaded=True)
        self.driver.back()
    
    def ConvertNodesToXpaths(self, elements:list[BeautifulSoup]):
        return [self.GetXpath(node) for node in elements] 


    '''
    Function for finding elements with sources, on which we can click
    to do next step.
        Args:
            doc:str - particular html document for finding clickable elements
            base_sources:list[str] - sources for finding elements which starts from something uri in the sources
        Return:
            elements:list[str] - list of xpaths for each suitable element
    '''
    def FindClickableElements(self, doc:str, base_sources:list[str])->list[str]:
        doc = BeautifulSoup(doc, features='html.parser')
        elements_nodes = []
        for partial_link in base_sources:
            nodes = self.FindElementWithSource(doc, partial_link)
            elements_nodes.extend(nodes)
        return elements_nodes

    '''
    Function for finding clickable elements with particular sources.
        Args:
            parent_node:BeautifulSoup - object in which we will finding clickable objects
            source:str - same as base_sources in FindClickableElements but it's particular source
        Return:
            nodes:list - list with elements in BeautifulSoup type 
    '''
    def FindElementWithSource(self, parent_node, source):
        nodes = []
        def FilterSource(item):
            if not item:
                return False
            if item.startswith(source):
                if item in self.history:
                    return False
                else:
                    #it's mean, that we seen this page, and don't want check this source in future
                    #http://www.ufcstats.com/event-details/56ec58954158966a
                    self.history.append(item)
                    return True
            return False
        for attr in self.particular_attr:
            nodes.extend(parent_node.find_all(attrs = {attr: FilterSource}))
        return nodes
    
    def Filtration(self, elements, source):
        if self.filters and source in self.filters:
            elements = self.filters[source].Filtration(elements)
        return elements
    
    '''
    Change self.page_processed function
        Args:
            page_processed: same as in __init__
    '''
    def setPageProcessed(self, page_processed: Callable[[str, str]]):
        self.page_processed = page_processed

    '''
    Function for extraction part of xpath from particular BeautifulSoup object
        Args:
            node: - 
        Return:
            if node doesn't have parent - node.name
            else string with parent with index of node in xpath style 
    '''
    def __GetElement(self, node):
        previous_siblings = node.find_previous_siblings(node.name)
        length = len(list(previous_siblings)) + 1
        if length > 1:
            return '%s[%s]' % (node.name, length)
        else:
            return node.name

    '''
    Function for extracton xpath to node.
        Args:
            node: particular node, xpath of which we want find
        Return:
            string xpath which is corresponded to node 
    '''
    def GetXpath(self, node):
        path = [self.__GetElement(node)]
        for parent in node.parents:
            if parent.name == 'body':
                break
            path.insert(0, self.__GetElement(parent))
        return './/' + '/'.join(path)


