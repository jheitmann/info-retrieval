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
Shunting_yard algorithm that parses boolean queries. 
Based on pseudo code given at https://en.wikipedia.org/wiki/Shunting-yard_algorithm
"""

def shunting_yard(query):
    operators_precedence = {'OR': 1, 'AND': 2, 'OR': 3, 'NOT': 4, '(': 5, ')': 5}
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


def last(stack):
    length = len(stack)
    return stack[length - 1]

def is_operator(token):
    return token == 'AND' or token == 'OR' or token == 'NOT'

def is_bracket(token):
    return token == '(' or token == ')'

def is_left_associative(token):
    return token == 'AND' or token == 'OR'



"""""
    Reads the file "queries_file_name" which contains a query by line and transform it in a list of queries where
    the tokens are posting lists
"""""
def prepare_queries(queries_file_name, postings_file_name, dictionary):
    output = []
    queries = open(queries_file_name, "r")
    postings = open(postings_file_name, "r")
    postings_cache = {}
    for line in queries.read().splitlines():
        prepared_query = []
        splitted = line.split(' ')
        for term in splitted:
            if is_operator(term):
                prepared_query.append(term)
            else:
                if(term[0] == '('):
                    term = term[1:len(term)]
                    prepared_query.append('(')
                right_parenthesis = False
                if(term[len(term)-1] == ')'):
                    term = term[0:len(term)-1]
                    right_parenthesis = True
                token = stem_and_casefold(term)
                offset = dictionary[token][1]
                # this posting list has not already been read from disk thus we cache it for efficiency
                if not offset in postings_cache:
                    postings.seek(offset)
                    line = postings.readline()
                    line = line[:-1] #TODO DO MANUALLY
                    postings_cache[offset] = posting_list(line)
                posting = postings_cache[offset]
                prepared_query.append(posting)
                if right_parenthesis:
                    prepared_query.append(")")
                #print(token+" : " + str(posting.to_string()))
        post_fixed_prepared_query = shunting_yard(prepared_query)
        output.append(post_fixed_prepared_query)
    queries.close()
    postings.close()
    return output

"""""
    Evaluates a post-fix expression where the operands are roots of linked lists and the operators are boolean
"""""
def evaluate(query, corpus):
    stack = []
    for token in query:
        if is_operator(token):
            if token == 'AND' :
                result = and_op(stack.pop(), stack.pop())
            if token == 'OR' :
                result = or_op(stack.pop())
            if token == 'NOT' :
                result = not_op(stack.pop(), corpus)
            stack.append(result)
        else:
            stack.append(token)
    return stack.pop()

def and_op_skip(postings1, postings2):
    result = ""
    element1 = postings1.next()
    element2 = postings2.next()

    while element1 is not None and element2 is not None:

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

        else:
            result += new_document(0, element1)
            element1 = postings1.next()
            element2 = postings2.next()

    return posting_list(result)

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
            result += new_document(0, element1)
            element1 = postings1.next()
            element2 = postings2.next()

    return posting_list(result)

def not_op(postings1, corpus):
    # we assume that postings1 is a subset of corpus
    result = ""
    postings1.rewind()
    postings2 = posting_list(corpus)

    element1 = postings1.next()
    element2 = postings2.next()

    if element1 is None:
        return postings2

    while element1 is not None or element2 is not None:

        if element2 is None or (element1 is not None and element1 < element2):
            print("Error this case shouldn't happen")
            element1 = postings1.next()

        elif element1 is None or (element2 is not None and element1 > element2):
            result += new_document(0, element2)
            element2 = postings2.next()

        else:
            element1 = postings1.next()
            element2 = postings2.next()

    return posting_list(result)

def or_op(postings1, postings2):
    result = ""
    postings1.rewind()
    postings2.rewind()
    element1 = postings1.next()
    element2 = postings2.next()

    if element1 is None:
        return postings2
    if element2 is None:
        return postings1

    while element1 is not None or element2 is not None:

        if element2 is None or (element1 is not None and element1 < element2):
            result += new_document(0, element1)
            element1 = postings1.next()

        elif element1 is None or (element2 is not None and element1 > element2):
            result += new_document(0, element2)
            element2 = postings2.next()

        else:
            result += new_document(0, element1)
            element1 = postings1.next()
            element2 = postings2.next()

    return posting_list(result)


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

# term -> (doc_freq, offset_in_bytes)
def prepare_dictionary(dictionary_file_name):
    file = open(dictionary_file_name, "r")
    dictionary = pickle.load(file)
    return dictionary

def search(dictionary_file_name, postings_file_name, queries_file_name, file_of_output_name):
    dictionary = prepare_dictionary(dictionary_file_name)
    queries = prepare_queries(queries_file_name, postings_file_name, dictionary)
    output = open(file_of_output_name, "w")

    for query in queries:
        output.write(str(evaluate(query, dictionary[DOC_LIST]).to_string())+"\n")
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