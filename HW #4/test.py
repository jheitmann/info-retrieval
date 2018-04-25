#!/usr/bin/python
import re
import nltk
import sys
import getopt
import linecache
import tempfile
import math
import csv
import os
import time
try:
   import cPickle as pickle
except:
   import pickle
from os import listdir
from tools_bi import *
from nltk.corpus import stopwords
from nltk.tokenize import RegexpTokenizer

csv.field_size_limit(sys.maxsize)

documents = [1620199, 2042299, 2124533, 2143694, 2144873, 2145623, 2145679, 2145727, 2145765, 2146284, 
			 2146366, 2147157, 2147817, 2147842, 2147910, 2148085, 2148306, 2148560, 2148915, 2149152, 
			 2149367, 2149531, 2149600, 2149658, 2150015, 2151343, 2152772, 2152777, 2152882, 2152897, 
			 2153112, 2153302, 2154445, 2155415]

print "ACTUAL\n"

f = open("dictionary.txt", 'r')
dictionary = pickle.load(f)
overtaken = dictionary[u'overtaken']
offset = overtaken[2]
f2 = open("postings.txt", 'r')
f2.seek(offset)
line = f2.readline()
pl = Postings(line)
for node in pl:
	print "docID and hash: " + str(get_docID(node)) + ", " + str(get_word_hash(node)) + '\n'

print "=================================\n"

print "THEORETICAL\n"

with open("dataset.csv", 'rb') as csvfile: # Scan all the documents
	law_reports = csv.reader(csvfile, delimiter=',', quotechar='"')
	law_reports.next() # Explain (first line contains tags)

	for rep_nbr, report in enumerate(law_reports):
		if rep_nbr == 1000:
			break

		docID = int(report[0]) # Extract docID

		if docID in documents:
			
			#print("Report being processed: " + str(docID))
			title = report[1].decode('UTF8').encode('ASCII', "ignore")  # Extract content, encode to ASCII
			content = report[2].decode('UTF8').encode('ASCII',"ignore") # Extract content, encode to ASCII
			date =  report[3].decode('UTF8').encode('ASCII',"ignore") # Extract content, encode to ASCII
			court = report[4].decode('UTF8').encode('ASCII',"ignore") # Extract content, encode to ASCII
			
			uni_words=[]
			#tokens = nltk.word_tokenize(content)
			content = title + " " + content + " " + date + " " + court

			#spans = nltk.tokenize.WhitespaceTokenizer().span_tokenize(content)
			# Yield the relevant slice of the input string representing each individual token in the sequence
			#tokens = [content[begin: end] for (begin, end) in spans]

			tokenizer = RegexpTokenizer(r'\w+')
			uni_words = tokenizer.tokenize(content)
			uni_words = [stem_and_casefold(term) for term in uni_words]

			bi_words = zip(uni_words,uni_words[1:])

			for t1,t2 in bi_words:
				if t1 == u'overtaken' and t1 < t2:
					print "docID and hash: " + str(docID) + ", " + str(unpack_string(hash32(t2)))+ '\n'
					print "other = " + t2 + '\n'
				elif t2 == u'overtaken' and t1 >= t2:
					print "docID and hash: " + str(docID) + ", " + str(unpack_string(hash32(t1))) + '\n'
					print "other = " + t1 + '\n'