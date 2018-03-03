#!/usr/bin/python
import re
import nltk
import sys
import getopt
from tools import *
""" 
Shunting_yard algorithm that parses boolean queries. 
Based on pseudo code given at https://en.wikipedia.org/wiki/Shunting-yard_algorithm
"""

def shunting_yard(query):
    operators_precedence = {'OR': 1, 'AND': 2, 'OR': 3, '(': 4, ')': 4}
    # operators_precedence = {'-': 2, '+': 2, '/': 3, 'x': 3, '^': 4, '(': 5, ')': 5}
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
    #return token == '-' or token == '+' or token == '/' or token == '^' or token == 'x'

def is_bracket(token):
    return token == '(' or token == ')'

def is_left_associative(token):
    return token == 'AND' or token == 'OR'
    #return token == '-' or token == '+' or token == '/' or token == 'x'

"""""
    Transforms a post-fix boolean expression with raw tokens as operands into an expression with the tokens
    replaced by the corresponding posting lists
"""""

def prepare_query(query):
    output = []
    for term in query:
        if is_operator(term):
            output.append(term)
        else:
            token = tools.tokenize(term)
            output.append(dictionnary(token))
    return output

"""""
    Reads the file "queries_file_name" which contains a query by line and transform it in a list of queries where
    the tokens are posting lists
"""""
def prepare_queries(queries_file_name):
    output = []
    queries = open(queries_file_name, "r")
    for line in queries:
        output.append(prepare_query(line))
    close(queries)
    return output

"""""
    Evaluates a post-fix expression where the operands are roots of linked lists and the operators are boolean
"""""
def evaluate(query):
    stack = []
    for token in query:
        if is_operator(token):
            if token == 'AND' :
                result = and_op(stack.pop(), stack.pop())
            if token == 'OR' :
                result = or_op(stack.pop())
            if token == 'NOT' :
                result = not_op(stack.pop())
            stack.append(result)
        else:
            stack.append(token)
    return stack.pop()

def and_op(postings1, postings2):
    #TODO
    return None

def not_op(postings):
    #TODO
    return None

def or_op(postings1, postings2):
    result = []

    element1 = postings1.next()
    element2 = postings2.next()

    if element1 is None:
        return postings2
    if element2 is None:
        return postings1

    while element1 is not None or element2 is not None:

        if element2 is None or (element1 is not None and element1 < element2):
            result.append(element1)
            element1 = postings1.next()

        elif element1 is None or (element2 is not None and element1 > element2):
            result.append(element2)
            element2 = postings2.next()

        else:
            result.append(element1)
            element1 = postings1.next()
            element2 = postings2.next()

    return result


class posting_list(object):
    pointer = 0
    list = []

    def __init__(self, list):
        self.list = list
        return

    def rewind(self):
        self.pointer = 0

    def next(self):
        if not self.pointer < len(self.list):
            return None

        element = unpack_string(self.list[self.pointer+1:self.pointer+5], 4)
        if self.skip_pointer() is not None:
            self.pointer += 9
        else:
            self.pointer += 5
        return element

    def skip_pointer(self):
        if unpack_string(self.list[self.pointer], 1) == 0:
            return None
        return unpack_string(self.list[self.pointer + 5: self.pointer + 5 + 4], 4)

def search(dictionnary, postings_file_name, queries, file_of_output_name):
    output = open(file_of_output_name, "w")
    for query in queries:
        output.write(evaluate(query))
    close(output)


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

p1 = posting_list('\x01\x00\x00\x00\x07\x00\x00\x00\x03\x00\x00\x00\x00\x08')
p2 = posting_list('\x01\x00\x00\x00\x07\x00\x00\x00\x03\x00\x00\x00\x00\x09')
p = or_op(p1,p2)
print(p)