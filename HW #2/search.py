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

""" 
    Shunting_yard algorithm that parses boolean expressions in in-fix mode to post-fix (reverse polish notation). 
    Based on the pseudo code given at https://en.wikipedia.org/wiki/Shunting-yard_algorithm
    
    - The expressions can only use the following operators : 'OR', 'AND', 'NOT', '(', ')'
    - Operands and operators must be separated by a space
    
    Example of a correct expression : 'windows and ( xp or vista )'
"""
def shunting_yard(query):
    operators_precedence = {'OR': 1, 'AND': 2, 'NOT': 3, '(': 4, ')': 4}
    output = []
    operator_stack = []
    for token in query:
        if not is_operator(token) and not is_bracket(token):
            output.append(token)
        if is_operator(token):
            while not len(operator_stack) == 0 and ((operators_precedence[last(operator_stack)] > operators_precedence[
                    token] or (operators_precedence[last(operator_stack)] == operators_precedence[
                    token] and is_left_associative(token))) and not last(operator_stack) == '('):
                output.append(operator_stack.pop())
            operator_stack.append(token)
        if token == '(':
            operator_stack.append(token)
        if token == ')':
            while not last(operator_stack) == '(':
                output.append(operator_stack.pop())
            operator_stack.pop()
    while not len(operator_stack) == 0:
        output.append(operator_stack.pop())
    return output

""" 
    Returns the last element of a stack (python list)
"""
def last(stack):
    length = len(stack)
    return stack[length - 1]

""" 
    Returns whether the given token (python string) is an operator
"""
def is_operator(token):
    return token == 'AND' or token == 'OR' or token == 'NOT'

""" 
    Returns whether the given token (python string) is a bracket
"""
def is_bracket(token):
    return token == '(' or token == ')'

"""
    Return whether the given token (python string) is a left associative operator (NOT operator is right associative)
"""
def is_left_associative(token):
    return token == 'AND' or token == 'OR'

"""""
    Reads the file "queries_file_name" which contains one query at each line and outputs a list containing
    the query in post-fix notation, where the terms have been stemmed and case-folded and then replaced
    by their corresponding posting-list as found from the inverted index.
"""""
def prepare_queries(queries_file_name, postings_file_name, dictionary_file_name):
    # output list of queries
    queries = []

    raw_queries = open(queries_file_name, "r")
    postings = open(postings_file_name, "r")

    # the dictionary is loaded from file using the pickle library
    serialized_dictionary = open(dictionary_file_name, "r")
    dictionary = pickle.load(serialized_dictionary)
    serialized_dictionary.close()

    # the postings cache avoids retrieving the same postings list from disk (costly) multiple times
    postings_cache = {}

    # each query in the queries_file is traversed
    for line in raw_queries.read().splitlines():
        prepared_query = []
        split = line.split(' ')

        # each word in the query is traversed, a word can either be a term (e.g 'bill') or an operator (e.g 'AND')
        for word in split:

            # if the word is an operator, we leave it as it is.
            if is_operator(word):
                operator = word
                prepared_query.append(operator)

            # if the word is a term, we need to reduce it (stemming, case-folding, etc)
            # and replace it by the corresponding posting list
            else:
                term = word

                # we need to separate terms and parenthesis (=add space).
                # for example 'windows and (xp or vista)' should be replaced by 'windows and ( xp or vista )'
                # this is needed to ease the work of the shunting-yard algorithm
                if(term[0] == '('):
                    term = term[1:len(term)]
                    prepared_query.append('(')
                right_parenthesis = False
                if(term[len(term)-1] == ')'):
                    term = term[0:len(term)-1]
                    right_parenthesis = True

                # the term is reduced in the same way as in the indexing part
                term = stem_and_casefold(term)

                # the position in the file of the posting-list corresponding to a term is given by the
                # offset (= pointer) stored in the dictionary (= inverted index)
                if term in dictionary:
                    offset = dictionary[term][1]

                    # this posting list has not already been read from disk thus we cache it for efficiency
                    if offset is not None and not offset in postings_cache:  # TODO offset not in instead of not offset in
                        postings.seek(offset)
                        line = postings.readline()
                        line = line[:-1]  # TODO DO MANUALLY
                        postings_cache[offset] = posting_list(line)

                    posting = postings_cache[offset]

                # if the term is not in the training corpus the corresponding posting-list is empty
                else:
                    postings = posting_list([])

                # we append the term to the query
                prepared_query.append(posting)

                # if there is a right parenthesis we separate it from the term (= add space)
                if right_parenthesis:
                    prepared_query.append(")")

        # we perform the shunting-yard algorithm on the query to transform it from an
        # in-fix expression to a post-fix expression
        post_fixed_prepared_query = shunting_yard(prepared_query)

        # the query is appended to the list of queries
        queries.append(post_fixed_prepared_query)

    raw_queries.close()
    postings.close()

    return queries

"""""
    Evaluates a post-fix expression where the operands are roots of linked lists and the operators are boolean
    The pseudo code algorithm is given at https://en.wikipedia.org/wiki/Reverse_Polish_notation
"""""
def evaluate(query, corpus):
    stack = []
    for token in query:
        if is_operator(token):
            if token == 'AND' :
                result = and_op(stack.pop(), stack.pop())
            if token == 'OR' :
                result = or_op(stack.pop(), stack.pop())
            if token == 'NOT' :
                result = not_op(stack.pop(), posting_list(corpus))
            stack.append(result)
        else:
            stack.append(token)
    return stack.pop()

"""""
    AND operation between 2 posting lists encapsulated in the custom class "posting_list"
    the algorithm follows the idea of your typical linked-list merge algorithm
"""""
def and_op_skip(postings1, postings2):
    result = ""
    postings1.rewind()
    postings2.rewind()
    element1 = postings1.next()
    element2 = postings2.next()

    # as long as we did not reach the end a both lists
    while element1 is not None and element2 is not None:

        # if the element1 is smaller than element2 we either replace element1 by the next one in the list or
        # replace it by the one pointed by the skip pointer if is possible
        if element1 is not None and element1 < element2:
            skip_pointer = postings1.skip_pointer()
            if skip_pointer:
                skip_value = postings1.value_at(skip_pointer)
                if skip_value <= element2:
                    element1 = skip_value
                    postings1.jump(skip_pointer)
                else:
                    element1 = postings1.next()
            else:
                 element1 = postings1.next()

        # symmetric case of the previous one :
        # if the element2 is smaller than element1 we either replace element2 by the next one in the list or
        # replace it by the one pointed by the skip pointer if is possible
        elif element2 is not None and element1 > element2:
            skip_pointer = postings2.skip_pointer()
            if skip_pointer:
                skip_value = postings2.value_at(skip_pointer)
                if skip_value <= element1:
                    element2 = skip_value
                    postings2.jump(skip_pointer)
                else:
                    element2 = postings2.next()
            else:
                element2 = postings2.next()

        # in this case both elements are the same, hence this element has to be added to the result
        else:
            result += new_node(0, element1)
            element1 = postings1.next()
            element2 = postings2.next()

    return posting_list(result)

#TODO delete this method and replace it by the one that uses skips pointers
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

"""""
    NOT operation on 1 posting list encapsulated in the custom class "posting_list"
    the algorithm follows the idea of your typical linked-list merge algorithm using
    the corpus (posting-list containing every document). Corpus is a posting-list
    containing every term from the data set
"""""
def not_op(postings1, corpus):
    # we assume that postings1 is a subset of corpus
    result = ""
    postings1.rewind()
    postings2 = corpus
    postings2.rewind

    # if postings1 is empty, then its inverse is the whole corpus
    if element1 is None:
        return postings2

    element1 = postings1.next()
    element2 = postings2.next()

    # as long as we haven't reached the end of both lists
    while element1 is not None or element2 is not None:

        # since the corpus contains every element from postings1 the case where
        # element1 < element2 is not possible
        if element2 is None or (element1 is not None and element1 < element2):
            print("Error this case shouldn't happen")
            element1 = postings1.next()

        # if element2 < element1 then it means that element2 appears in the corpus
        # and not in the postings1, hence it is added to the output and we jump to
        # the next element
        elif element1 is None or (element2 is not None and element1 > element2):
            result += new_node(0, element2)
            element2 = postings2.next()

        # in this case both elements are the same, hence they are not added to the output
        # and we jump the the next element of each list
        else:
            element1 = postings1.next()
            element2 = postings2.next()

    return posting_list(result)

"""""
    OR operation between 2 posting lists encapsulated in the custom class "posting_list"
    the algorithm follows the idea of your typical linked-list merge algorithm
"""""
def or_op(postings1, postings2):
    result = ""
    postings1.rewind()
    postings2.rewind()
    element1 = postings1.next()
    element2 = postings2.next()

    # if the first posting list is empty, we can output the second one
    if element1 is None:
        return postings2

    # symmetrically, if the second posting list is empty, we can output the first one
    if element2 is None:
        return postings1

    # as long as we haven't reached the end of both lists we go through both lists and output every element
    # appearing in any of the list once
    while element1 is not None or element2 is not None:

        if element2 is None or (element1 is not None and element1 < element2):
            result += new_node(0, element1)
            element1 = postings1.next()

        elif element1 is None or (element2 is not None and element1 > element2):
            result += new_node(0, element2)
            element2 = postings2.next()

        else:
            result += new_node(0, element1)
            element1 = postings1.next()
            element2 = postings2.next()

    return posting_list(result)

"""""
    This class encapsulates a raw posting-list and offers a convenient interface to interact with the posting-list
"""""
class posting_list(object):
    pointer = 0
    list = []
    def __init__(self, list):
        self.list = list
        return

    def jump(self, position):
        self.pointer = position

    def rewind(self):
        self.jump(0)

    def value_at(self, position):
        return unpack_string(self.list[position+1:position+9])

    def next(self):
        if not self.pointer < len(self.list):
            return None
        element = unpack_string(self.list[self.pointer+1:self.pointer+9])
        if self.skip_pointer() is not None:
            self.pointer += 17
        else:
            self.pointer += 9
        return element

    def skip_pointer(self):
        if unpack_string(self.list[self.pointer]) == 0:
            return None
        return unpack_string(self.list[self.pointer + 5: self.pointer + 5 + 4])

    def to_string(self):
        self.rewind()
        result = ""
        element = self.next()
        while element is not None:
            result += str(element)
            element = self.next()
            if element is not None:
                result += " "
        return result

def search(dictionary_file_name, postings_file_name, queries_file_name, file_of_output_name):
    queries = prepare_queries(queries_file_name, postings_file_name, dictionary_file_name)
    output = open(file_of_output_name, "w")

    #EXPLAIN THIS DODO
    postings = open(postings_file_name, "r")
    postings.seek(dictionary[DOC_LIST][1])
    corpus = postings.readline()
    corpus = corpus[:-1]  # TODO DO MANUALLY
    postings.close()
    for query in queries:
        output.write(str(evaluate(query, corpus).to_string())+"\n")
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

search(dictionary_file, postings_file, file_of_queries, file_of_output)