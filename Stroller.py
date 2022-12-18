from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions

from collections.abc import Callable
from bs4 import BeautifulSoup

class BaseStoller:
    '''
    
    Args:
        transition_graph:dict - it's graph which contain url for transition from page1 to page2
        when exist possobility for this transition on page1.
        transition_graph don't need to contain particulary url. keys should contain base part of source.
        Transition on next page happens if part uri contain this base part of source.
        particular_attr:list[str] - contain attributes in which will searching sources from transition_graph
    '''
    def __init__(self, transition_graph:dict,
                       particular_attr:list[str],
                       page_processed: Callable[[str, str]],) -> None:
        self.transition_graph = transition_graph
        self.page_processed = page_processed
        self.particular_attr = particular_attr
        self.set_options()
        self.set_driver()

        self.history = [] #contain pages which is viewed

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

    def StartWandering(self, transition_graph = None):
        if not transition_graph:
            transition_graph = self.transition_graph
        self.Step(transition_graph)
    
    def Step(self, transition_graph, page_is_loaded = False):
        for current_page, next_transition in transition_graph.items():
            self.history.append(current_page)
            if not page_is_loaded:
                self.driver.get(current_page)
            self.page_processed(current_page, self.driver.page_source)
            if next_transition: # if next page is not none. If page is None that it's mean stop 
                base_sources = list(next_transition.keys())
                elements = self.FindClickableElements(self.driver.page_source, base_sources) # if clickable elements didn't exist
                #then recursion end.
                #If we seen source (contained in history)
                for node_xpath in elements:
                    pl_elements = WebDriverWait(self.driver, 5, self.driver.find_element_by_xpath(node_xpath)).until(
                                expected_conditions.presence_of_element_located((By.XPATH, node_xpath))
                    )
                    self.StepClick(pl_elements, next_transition)

    def StepClick(self, element, transition_graph):
        element.click()
        self.Step(transition_graph, page_is_loaded=True)
        self.driver.back()

    def FindClickableElements(self, doc:str, base_sources:list[str])->list[WebElement]:
        doc = BeautifulSoup(doc, features='html.parser')
        elements = []
        for partial_link in base_sources:
            nodes = self.FindElementWithSource(doc, partial_link)
            for node in nodes:
                node_xpath = self.GetXpath(node)
                elements.append(node_xpath)
        return elements

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

    def __GetElement(self, node):
        previous_siblings = node.find_previous_siblings(node.name)
        length = len(list(previous_siblings)) + 1
        if length > 1:
            return '%s[%s]' % (node.name, length)
        else:
            return node.name

    def GetXpath(self, node):
        path = [self.__GetElement(node)]
        for parent in node.parents:
            if parent.name == 'body':
                break
            path.insert(0, self.__GetElement(parent))
        return './/' + '/'.join(path)


