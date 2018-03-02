#!/usr/bin/python
import re
import nltk
import sys
import getopt

def tokenize(word_to_process): 
	return word_to_process

class Root(object):
    def __init__(self, docID):
        self.head = Element(docID)
        self.last = self.head
        return

    def append_element(self, element):
        self.last.add_next(element)
        self.last = element
        return

    def insert_after(self, predecessor, element): # Needs to be implemented
        return 



class Element(object):
    def __init__(self, docID):
        self.docID = docID
        return

    def add_next(self, element):
        self.next = element
        return

    def add_skip_pointer(self, element):
	    self.skip_pointer = element
	    return

    