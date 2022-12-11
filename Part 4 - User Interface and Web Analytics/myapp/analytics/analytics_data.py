import json
import random


class AnalyticsData:
    """
    An in memory persistence object.
    Declare more variables to hold analytics tables.
    """ 
    # Statistics for queries
    fact_terms = dict([]) # key = term | value = count
    fact_number_terms = dict([]) # key = query | value = query lenght
    fact_query_times = dict([]) # key = query | value = count
    
    # Statistics for results (documents)
    fact_clicks = dict([]) # fact_clicks is a dictionary with the click counters: key = doc id | value = click counter
    fact_rankings = dict([]) # key = doc id | value = counter (only top 10 most clicked docs)
    fact_queries = dict([]) # key = doc id | value = list of queries
    fact_dwell_time = dict([]) # key = doc id | value = total time spend inside the document

    # Statistics for user contex
    fact_browser = dict([]) # key = browser | value = count
    fact_OS = dict([]) # key = Operating System | value = count
    fact_time = dict([]) # key = Hour | value = count
    fact_date = dict([]) # key = Date | value = count
    fact_ip = dict([]) # key = IP | value = count
    
    # Statistics for sessions
    fact_num_queries = dict([]) # key = session | value = number of searches
    fact_num_detail = dict([]) # key = session | value = number of clicked documents

    
    def save_query_terms(self, terms: str) -> int:
        print(self)
        return random.randint(0, 100000)


class ClickedDoc:
    def __init__(self, doc_id, description, counter):
        self.doc_id = doc_id
        self.description = description
        self.counter = counter
        
    def to_json(self):
        return self.__dict__

    def __str__(self):
        """
        Print the object content as a JSON string
        """
        return json.dumps(self)
