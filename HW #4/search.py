    #!/usr/bin/python
import re
import nltk
import sys
import getopt
from tools import *
try:
   import cPickle as pickle
except:
   import pickle
import time
from math import log10
from nltk.corpus import wordnet as wn #TODO how to correctly import for submission ?

def query_expansion(query):
    query_expanded = []
    print("Query before expansion : "+' '.join(query))
    for term in query:
        hypernym = ""
        synsets = wn.synsets(term.lower())
        if len(synsets) != 0:
            hypernyms = synsets[0].hypernyms()
            if len(hypernyms) != 0:
                hypernym = hypernyms[0].lemmas()[0].name().replace('_', ' ')
        query_expanded.append(term)
        if hypernym != "":
            query_expanded.append(hypernym)
    print("Query after expansion : "+' '.join(query_expanded))
    return query_expanded

# return whether a given query (in a list format) is boolean
# boolean query either contain the "AND" keyword or contain phrasal queries delimited by ""
# the special case of a boolean query with one word only is going to be considered to be a phrasal query
def is_boolean_query(query):
    for term in query:
        if term == 'AND' or term[0] == '"':
            return True
    return False

def read_query_from_file(queries_file_name):
    query_file = open(queries_file_name, "r")
    query = query_file.readline()[:-1].split()
    query_file.close()
    return query

def and_op(postings1, postings2):
    result = ""
    postings1.rewind()
    postings2.rewind()
    element1 = postings1.next()
    element2 = postings2.next()

    while element1 is not None and element2 is not None:
        if element1 is not None and element1 < element2:
            element1 = postings1.next()
        elif element2 is not None and element1 > element2:
            element2 = postings2.next()
        else:
            result += new_node(0, element1)
            element1 = postings1.next()
            element2 = postings2.next()

    return posting_list(result)

def evaluate_boolean_query(query, dictionary_mono, dictionary_bi, dictionary_tri, postings):
    return 0

def parse_boolean_query(query):
    parsed_query = []

    between_quotes = False
    phrase = ""
    for term in query:
        if term.startswith('"'):
            between_quotes = True
            phrase = term[1:]
        elif term.endswith('"'):
            between_quotes = False
            phrase += " "+term[:-1]
            parsed_query.append(phrase)
        else:
            if between_quotes == True:
                phrase += " "+term
            else:
                parsed_query.append(term)
    return parsed_query

"""
    Helper function that takes the name of a text file with free text queries, in which there is one query by line
    and returns a list of queries. (a query is also a list, thus the function returns a list of lists)
"""
def prepare_queries(queries_file_name):
    # output list of queries
    queries = []

    raw_queries = open(queries_file_name, "r")

    # each query in the queries_file is traversed
    for line in raw_queries:
        terms = nltk.word_tokenize(line)
        queries.append([stem_and_casefold(term) for term in terms])
    raw_queries.close()
    return queries

"""
    Helper function that finds the top 10 documents based on the cosine similarity based on the pseudo code provided
    in class.
"""
def cosine_score(query, postings, dictionary, length):

    scores = dict()
    N = len(length) #Already defined
    w_t_q = compute_w_t_q(query, dictionary, N)
    for term in query:
        if term in dictionary:
            posting_list = fetch_posting_list(term, dictionary, postings)
            for pair in posting_list:
                document = get_docID(pair)
                tf_t_d = get_tf(pair)
                w_t_d = 1 + log10(tf_t_d)
                scores[document] = scores.get(document, 0) + w_t_d * w_t_q[term] # use td_weight
    for document in scores:
        scores[document] = scores[document] / length[document]

    return top_k(scores)

"""
    returns a map from the terms in the query given in parameter to their corresponding weights in the query (tfxidf)
"""
def compute_w_t_q(query, dictionary, N):
    # PHASE 1 : count the number of occurrences of each term in the query (i.e compute the term frequency)
    tf = dict()
    for term in query:
        tf[term] = tf.get(term, 0) + 1

    # PHASE 2 : for each term, compute the log TF * IDF score.
    w_t_q = dict()
    for term in tf:
        w_t_q[term] = 0
        if term in dictionary:
            w_t_q[term] = td_weight(tf[term], dictionary[term][0], N)

    return w_t_q


"""
    Reads a posting list from file given a term and the dictionary
"""
def fetch_posting_list(term, dictionary, postings):
    offset = dictionary[term][1]
    postings.seek(offset)
    posting_list = Postings(postings.readline())
    return posting_list

"""
    Actual search function that finds the top k documents for each query and writes the results in a filte
"""
def search(dictionary_file_name, postings_file_name, queries_file_name, file_of_output_name):

    #the dictionary is loaded from file using the pickle library
    serialized = open(dictionary_file_name, "r")
    dictionary = pickle.load(serialized)
    length = pickle.load(serialized)
    serialized.close()

    # the output file containing the results of the queries, each result on a different line
    output = open(file_of_output_name, "w")

    # queries are prepared using the above defined helper function
    postings = open(postings_file_name, "r")
    queries = prepare_queries(queries_file_name)

    # every query is evaluated and the output written to the output file
    for query in queries:
        output.write(cosine_score(query, postings, dictionary, length) + '\n')#GET RID OF LAST LINE RETURN

    postings.close()
    output.close()


def usage():
    print
    "usage: " + sys.argv[0] + " -d dictionary-file -p postings-file -q file-of-queries -o output-file-of-results"


dictionary_file = postings_file = file_of_queries = output_file_of_results = None

try:
    opts, args = getopt.getopt(sys.argv[1:], 'd:p:q:o:')
except getopt.GetoptError, err:
    usage()
    sys.exit(2)

for o, a in opts:
    if o == '-d':
        dictionary_file = a
    elif o == '-p':
        postings_file = a
    elif o == '-q':
        file_of_queries = a
    elif o == '-o':
        file_of_output = a
    else:
        assert False, "unhandled option"

if dictionary_file == None or postings_file == None or file_of_queries == None or file_of_output == None:
    usage()
    sys.exit(2)

start = time.time()
# search(dictionary_file, postings_file, file_of_queries, file_of_output)

query = read_query_from_file(file_of_queries)
if is_boolean_query(query):
    print("The query is boolean")
    parsed_query = parse_boolean_query(query)
    print("The parsed boolean query is :")
    print(parsed_query)
else:
    print("The query is not boolean")
    query_expansion(query)

end = time.time()
print("Query time : "+str(end - start))