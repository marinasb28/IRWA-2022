import os
from json import JSONEncoder

# pip install httpagentparser
import httpagentparser  # for getting the user agent as json
from user_agents import parse
import nltk
from flask import Flask, render_template, session
from flask import request
import json
import datetime
import time
import random

from myapp.analytics.analytics_data import AnalyticsData, ClickedDoc
from myapp.search.load_corpus import load_corpus
from myapp.search.objects import Document, StatsDocument, StatsQuery, StatsSession
from myapp.search.search_engine import SearchEngine
from myapp.search.algorithms import create_index_tfidf

# *** for using method to_json in objects ***
def _default(self, obj):
    return getattr(obj.__class__, "to_json", _default.default)(obj)


_default.default = JSONEncoder().default
JSONEncoder.default = _default

# end lines ***for using method to_json in objects ***

# instantiate the Flask application
app = Flask(__name__)

# random 'secret_key' is used for persisting data in secure cookie
app.secret_key = 'afgsreg86sr897b6st8b76va8er76fcs6g8d7'
# open browser dev tool to see the cookies
app.session_cookie_name = 'IRWA_SEARCH_ENGINE'

# instantiate our search engine
search_engine = SearchEngine()

# instantiate our in memory persistence
analytics_data = AnalyticsData()

# print("current dir", os.getcwd() + "\n")
# print("__file__", __file__ + "\n")
full_path = os.path.realpath(__file__)
path, filename = os.path.split(full_path)
# print(path + ' --> ' + filename + "\n")
# load documents corpus into memory.
file_path = path + "/tweets-data-who.json"

# file_path = "../../tweets-data-who.json"
corpus = load_corpus(file_path)
print("loaded corpus. first elem:", list(corpus.values())[0])

session_id = 'Session' + str(random.randint(0, 100000))

# Home URL "/"
@app.route('/')
def index():
    session['end'] = time.time()
    
    print("starting home url /...")

    # flask server creates a session by persisting a cookie in the user's browser.
    # the 'session' object keeps data between multiple requests
    session['some_var'] = "IRWA 2021 home"

    user_agent = request.headers.get('User-Agent')
    print("Raw user browser:", user_agent)

    user_ip = request.remote_addr
    agent = httpagentparser.detect(user_agent)
    user_os = agent['os']['name']
    user_browser = agent['browser']['name']
    date_time = datetime.datetime.now()
    date = str(date_time.day) + '/' + str(date_time.month) + '/' + str(date_time.year)
    hour = str(date_time.hour)
    
    print("Remote IP: {} - JSON user browser {}".format(user_ip, agent))
    print(session)

    # store data in statistics tables
    if user_browser in analytics_data.fact_browser.keys():
        analytics_data.fact_browser[user_browser] += 1
    else:
        analytics_data.fact_browser[user_browser] = 1
    
    if user_ip in analytics_data.fact_ip.keys():
        analytics_data.fact_ip[user_ip] += 1
    else:
        analytics_data.fact_ip[user_ip] = 1
    
    if user_os in analytics_data.fact_OS.keys():
        analytics_data.fact_OS[user_os] += 1
    else:
        analytics_data.fact_OS[user_os] = 1
    
    if date in analytics_data.fact_date.keys():
        analytics_data.fact_date[date] += 1
    else:
        analytics_data.fact_date[date] = 1
    
    if hour in analytics_data.fact_time.keys():
        analytics_data.fact_time[hour] += 1
    else:
        analytics_data.fact_time[hour] = 1
    
    
    try:
        dwell_time = session['end'] - session['start']
        if session['last_doc_id'] in analytics_data.fact_dwell_time.keys():
            analytics_data.fact_dwell_time[session['last_doc_id']] += dwell_time
        else:
            analytics_data.fact_dwell_time[session['last_doc_id']] = dwell_time
    except:
        pass

    return render_template('index.html', page_title="Welcome")

@app.route('/search', methods=['POST'])
def search_form_post():
    search_query = request.form['search-query']
    terms = search_query.split()

    # store data in statistics tables
    for term in terms:
        if term in analytics_data.fact_terms.keys():
            analytics_data.fact_terms[term] += 1
        else:
            analytics_data.fact_terms[term] = 1

    if search_query not in analytics_data.fact_number_terms.keys():
        analytics_data.fact_number_terms[search_query] = len(terms)
    
    if search_query in analytics_data.fact_query_times.keys():
        analytics_data.fact_query_times[search_query] += 1
    else:
        analytics_data.fact_query_times[search_query] = 1
    
    if session_id in analytics_data.fact_num_queries.keys():
        analytics_data.fact_num_queries[session_id] += 1
    else:
        analytics_data.fact_num_queries[session_id] = 1
    
    session['last_search_query'] = search_query

    search_id = analytics_data.save_query_terms(search_query)

    try:
        with open(path + '/index.json', 'rb') as index_file:
            index = json.load(index_file)
        with open(path + '/tf.json', 'rb') as tf_file:
            tf = json.load(tf_file)
        with open(path + '/idf.json', 'rb') as idf_file:
            idf = json.load(idf_file)
    except:
        index, tf, idf = create_index_tfidf(corpus, len(corpus))
        with open(path + '/index.json', 'w') as index_file:
            json.dump(index, index_file)
        with open(path + '/tf.json', 'w') as tf_file:
            json.dump(tf, tf_file)
        with open(path + '/idf.json', 'w') as idf_file:
            json.dump(idf, idf_file)
    results = search_engine.search(search_query, search_id, corpus, index, tf, idf)

    found_count = len(results)
    session['last_found_count'] = found_count

    print(session)

    return render_template('results.html', results_list=results, page_title="Results", found_counter=found_count)


@app.route('/doc_details', methods=['GET'])
def doc_details():
    session['start'] = time.time()
    # getting request parameters:
    #user = request.args.get('user')
    print("doc details session: ")
    print(session)

    res = session["some_var"]

    print("recovered var from session:", res)

    # get the query string parameters from request
    clicked_doc_id = int(request.args["id"])
    session['last_doc_id'] = clicked_doc_id
    p1 = int(request.args["search_id"])  # transform to Integer
    query = request.args["search_query"]
    print("click in id={}".format(clicked_doc_id))

    # store data in statistics tables
    if clicked_doc_id in analytics_data.fact_clicks.keys():
        analytics_data.fact_clicks[clicked_doc_id] += 1
        if query not in analytics_data.fact_queries[clicked_doc_id]:
            analytics_data.fact_queries[clicked_doc_id].append(query)
    else:
        analytics_data.fact_clicks[clicked_doc_id] = 1
        analytics_data.fact_queries[clicked_doc_id] = [query]
    
    if len(analytics_data.fact_rankings) < 10:
        analytics_data.fact_rankings[clicked_doc_id] = analytics_data.fact_clicks[clicked_doc_id]
    else:
        if analytics_data.fact_rankings[clicked_doc_id] > min(analytics_data.fact_rankings.values()):
            minimum = min(analytics_data.fact_rankings.values())
            docs = [docs for doc in analytics_data.fact_rankings.keys() if analytics_data.fact_rankings[doc]==minimum]
            analytics_data.fact_rankings.pop(docs[0])
            analytics_data.fact_rankings[clicked_doc_id] = analytics_data.fact_clicks[clicked_doc_id]
        else:
            analytics_data.fact_rankings[clicked_doc_id] = analytics_data.fact_clicks[clicked_doc_id]

    if session_id in analytics_data.fact_num_detail.keys():
        analytics_data.fact_num_detail[session_id] += 1
    else:
        analytics_data.fact_num_detail[session_id] = 1
    
    
    print("fact_clicks count for id={} is {}".format(clicked_doc_id, analytics_data.fact_clicks[clicked_doc_id]))
    return render_template('doc_details.html', item=corpus[clicked_doc_id])


@app.route('/stats', methods=['GET'])
def stats():
    """
    Show simple statistics example. ### Replace with dashboard ###
    :return:
    """

    docs = []
    queries = []

    for doc_id in analytics_data.fact_clicks:
        row: Document = corpus[int(doc_id)]
        count = analytics_data.fact_clicks[doc_id]
        if doc_id in analytics_data.fact_rankings.keys(): is_top10=True
        else: is_top10=False
        queries_related = analytics_data.fact_queries[doc_id]
        try: dwell_time = round(analytics_data.fact_dwell_time[doc_id], 2) 
        except: dwell_time=1
        doc = StatsDocument(row.id, row.title, row.description, row.doc_date, row.url, count, is_top10, queries_related, dwell_time)
        docs.append(doc)
    
    for query in analytics_data.fact_query_times:
        length = analytics_data.fact_number_terms[query]
        times_searched = analytics_data.fact_query_times[query]
        query = StatsQuery(query, length, times_searched)
        queries.append(query)

    print(analytics_data.fact_browser, analytics_data.fact_OS)    
    session_data = StatsSession(analytics_data.fact_browser, analytics_data.fact_OS, analytics_data.fact_ip, analytics_data.fact_time, analytics_data.fact_date, analytics_data.fact_num_queries, analytics_data.fact_num_detail)
    # simulate sort by ranking
    docs.sort(key=lambda doc: doc.count, reverse=True)
    return render_template('stats.html', clicks_data=docs, searched_queries=queries, session_data=session_data)
    

@app.route('/dashboard', methods=['GET'])
def dashboard():
    visited_docs = []
    print(analytics_data.fact_clicks.keys())
    for doc_id in analytics_data.fact_clicks.keys():
        d: Document = corpus[int(doc_id)]
        doc = ClickedDoc(doc_id, d.description, analytics_data.fact_clicks[doc_id])
        visited_docs.append(doc)

    # simulate sort by ranking
    visited_docs.sort(key=lambda doc: doc.counter, reverse=True)
    visited_ser = []
    for doc in visited_docs: 
        visited_ser.append(doc.to_json())
    return render_template('dashboard.html', visited_docs=visited_ser)


@app.route('/sentiment')
def sentiment_form():
    return render_template('sentiment.html')


@app.route('/sentiment', methods=['POST'])
def sentiment_form_post():
    text = request.form['text']
    nltk.download('vader_lexicon')
    from nltk.sentiment.vader import SentimentIntensityAnalyzer
    sid = SentimentIntensityAnalyzer()
    score = ((sid.polarity_scores(str(text)))['compound'])
    return render_template('sentiment.html', score=score)


if __name__ == "__main__":
    app.run(port=8088, host="0.0.0.0", threaded=False, debug=True)
