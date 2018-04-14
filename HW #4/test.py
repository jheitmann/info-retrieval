import re
import nltk
import sys
import getopt
import math
from tools import *
try:
   import cPickle as pickle
except:
   import pickle
import time


documents = [11036, 9389, 3801]

query = stem_and_casefold("profit")

for docID in documents:
	f = open(str(docID),'r')

	dictionary = {}
	for line in f:
		raw_terms = nltk.word_tokenize(line)
		terms = [stem_and_casefold(raw_term) for raw_term in raw_terms]
		for term in terms:
			dictionary[term] = dictionary.get(term, 0) + 1

	length = 0
	for term, freq in dictionary.items():
		score = 1+math.log10(freq)
		dictionary[term] = score
		length += score*score

	length = math.sqrt(length)

	res = dictionary[query]/length
	print "Score for doc " + str(docID) + " : " + str(res) + '\n'