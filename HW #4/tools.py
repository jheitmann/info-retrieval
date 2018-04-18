#!/usr/bin/python
import re
import nltk
import sys
import getopt
import math
import tempfile
import nltk
from nltk.stem.porter import *

ELEM_SIZE = 8  # Elem is either a docID or a term frequency
NODE_SIZE = 2 * ELEM_SIZE  # A node is a docID and a term frequency
stemmer = PorterStemmer()  # stem_and_casefold(word_to_process) uses this stemmer


# Applies the Porter Stemming algorithm, then case-folding
def stem_and_casefold(word_to_process):
    word = stemmer.stem(word_to_process)
    #word = word.lower()
    return word


# Returns the hexadecimal string of an int, using nbr_chars characters
def pack_bytes(n, nbr_chars):
    return format(n, "0" + str(nbr_chars) + "x")


# Returns the int value of the hexadecimal string s
def unpack_string(s):
    return int(s, 16)


# Returns a new node, with term frequency set to 1
def new_node(docID):
    return pack_bytes(docID, ELEM_SIZE) + pack_bytes(1, ELEM_SIZE)


# Returns the docID of a node
def get_docID(node):
    return unpack_string(node[:ELEM_SIZE])


# Returns the term frequency of a node
def get_tf(node):
    return unpack_string(node[ELEM_SIZE:])


"""
Given a node with a term frequency tf, returns a new node with identical 
docID and term frequency tf+1
"""
def updated_tf(node):
    incr_tf = get_tf(node) + 1
    return pack_bytes(get_docID(node), ELEM_SIZE) + pack_bytes(incr_tf, ELEM_SIZE)


# Returns the tf-idf score
def td_weight(term_frequency):
    if term_frequency == 0 or doc_frequency == 0:
        return 0
    else:
        return (1 + math.log10(term_frequency))


"""
The goal is to increment the term_frequency attribute of the last node in a 
given posting list (at line_number in file). To do so, we compute the offset 
of this last node in the file, seek() to this position, and overwrite it 
with an updated node.
"""
def update_last_node(file, line_number):
    with open(file, 'r+') as outfile:
        for i in range(line_number + 1):  # +1: line to modify also read
            next_posting_list = outfile.readline()

        last_node = Postings(next_posting_list).value_at(-1) # Fetches the last node
        # seek() to the position of last_node in file, +1: '\n' at the end of a line
        outfile.seek(-(NODE_SIZE + 1), 1) 
        outfile.write(updated_tf(last_node))


"""
In order to replace a specific line in a file, the subsequent lines must be 
overwritten. Hence this method stores the new line (that replaces the old one)
and the subsequent lines in a temporary file, then overwrites the initial file, 
starting at the line to be replaced.
"""
def update_posting_list(file, line_number, new_line):
    with open(file, 'r+') as outfile:
        fp = tempfile.TemporaryFile()
        fp.write(new_line)

        offset = 0  # Offset represents the position of the line to be replaced
        for i, line in enumerate(outfile):
            if i < line_number:
                offset += len(line)
            elif i > line_number:
                fp.write(line)

        fp.seek(0)
        outfile.seek(offset)
        for pl in fp:
            outfile.write(pl)
        fp.close()

"""
    tool functions to implement a max-heap on a given array A. Elements of A are (docID, score) pairs.
    the comparison is on score first, i.e (X, 4) > (Y, 3) and then on docID in case of tie but in
    reversed order i.e (3, 4) > (5, 4).
    from pseudo code given at https://courses.csail.mit.edu/6.006/fall10/handouts/recitation10-8.pdf
    and https://en.wikipedia.org/wiki/Binary_heap
"""
def build_max_heap(A):
    for i in range(len(A) / 2 - 1, -1, -1):
        max_heapify(A, i)


def max_heapify(A, i):
    heap_size = len(A)
    left = 2 * i + 1
    right = 2 * i + 2
    largest = i
    if left < heap_size and (
            A[left][1] > A[largest][1] or (A[left][1] == A[largest][1]) and A[left][0] < A[largest][0]):
        largest = left
    if right < heap_size and (
            A[right][1] > A[largest][1] or (A[right][1] == A[largest][1] and A[right][0] < A[largest][0])):
        largest = right

    if not largest == i:
        swap(A, i, largest)
        max_heapify(A, largest)


def swap(A, i, largest):
    temp = A[i]
    A[i] = A[largest]
    A[largest] = temp


def extract_max(A):
    if len(A) == 1:
        return A.pop()[0]
    max = A[0][0]
    A[0] = A.pop()
    max_heapify(A, 0)
    return max


def top_k(scores):
    A = scores.items()
    build_max_heap(A)
    result = ''
    k = 10
    if len(A) < k:
        k = len(A)
    for i in range(k):
        result += str(extract_max(A)) if result == '' else ' '+str(extract_max(A))
    return result

def extract_min(A):
    if len(A) == 1:
        return A.pop()[1]
    max = A[0][1]
    A[0] = A.pop()
    min_heapify(A, 0)
    return max

def min_heapify(A, i):
    heap_size = len(A)
    left = 2 * i + 1
    right = 2 * i + 2
    largest = i
    if left < heap_size and (
            A[left][1] < A[largest][1]:
        largest = left
    if right < heap_size and (
            A[right][1] < A[largest][1] :
        largest = right

    if not largest == i:
        swap(A, i, largest)
        max_heapify(A, largest)

def insert( A,key):
    
def increase_key(A,i,key):
    

"""
    This class encapsulates a raw posting-list and offers a convenient interface 
    to interact with it. A node in the posting-list has the following internal
    structure: [ docID (ELEM_SIZE chars) | term_frequency (ELEM_SIZE chars) ]
"""
class Postings(object):

    def __init__(self, posting_list):
        if (posting_list[-1:] == "\n"):
            posting_list = posting_list[:-1]  # [:-1]: '\n' ignored
        self.postings = posting_list
        self.nbr_nodes = len(posting_list) / NODE_SIZE  # Explain
        self.pointer = 0
        return

    def __iter__(self):
        return self

    # Makes iterating other postings possible
    def next(self):
        if self.pointer < (self.nbr_nodes * NODE_SIZE):
            next_node = self.postings[self.pointer:self.pointer + NODE_SIZE]
            self.pointer += NODE_SIZE
            return next_node
        else:
            raise StopIteration

    def next_node(self):
        try:
            return self.next()
        except StopIteration:
            return None

    # Jumps to the specified position in the list (relative position)
    def jump(self, position):
        if (position < self.nbr_nodes):
            self.pointer = position * NODE_SIZE

    # Jumps to the first node in the list
    def rewind(self):
        self.jump(0)

    """
    Allows us to directly access a certain node, negative position possible 
    (similar to list, i.e. if l = [...], l[-1]). Again, it is only a relative
    position (the (position+1)th node in the posting list), and doesn't 
    correspond to the actual position of this particular node in self.postings
    """
    def value_at(self, position):
        if position == -1:
            node = self.postings[-NODE_SIZE:]
            return node
        elif -nbr_nodes <= position < nbr_nodes:
            node = self.postings[position * NODE_SIZE:(position + 1) * NODE_SIZE]
            return node
        else:
            return None

    def to_string(self):
        return self.postings


""" 
Taken from: stackoverflow.com/questions/1063319/reversible-dictionary-for-python
A bidirectional dictionary (need to have bijective mapping)
"""
class BidirectionalDict(dict):
    def __setitem__(self, key, val):
        dict.__setitem__(self, key, val)
        dict.__setitem__(self, val, key)

    def __delitem__(self, key):
        dict.__delitem__(self, self[key])
        dict.__delitem__(self, key)
