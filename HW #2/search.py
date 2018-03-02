#!/usr/bin/python
import re
import nltk
import sys
import getopt

""" 
Shunting_yard algorithm that parses boolean queries. 
Based on pseudo code given at https://en.wikipedia.org/wiki/Shunting-yard_algorithm
"""

#operators_precedence = {'OR': 1, 'AND': 2, 'OR': 3, '(': 4, ')': 4}
operators_precedence = {'-': 2, '+': 2, '/': 3, 'x': 3, '^': 4, '(': 5, ')': 5}

def test():
    print("hi")
def shunting_yard(query):
    output = []
    operator_stack = []
    for token in query:
        print(operator_stack)
        if not is_operand(token) and not is_bracket(token):
            output.append(token)
        if is_operand(token):
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

def is_operand(token):
    #return token == 'AND' or token == 'OR' or token == 'NOT'
    return token == '-' or token == '+' or token == '/' or token == '^' or token == 'x'

def is_bracket(token):
    return token == '(' or token == ')'

def is_left_associative(token):
    #return token == 'AND' or token == 'OR'
    return token == '-' or token == '+' or token == '/' or token == 'x'
"""""
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
"""""