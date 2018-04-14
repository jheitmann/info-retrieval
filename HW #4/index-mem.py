#!/usr/bin/python
import re
import nltk
import sys
import getopt
import linecache
import tempfile
import math
import csv
try:
   import cPickle as pickle
except:
   import pickle
from os import listdir
from tools import *

def usage():
    print "usage: " + sys.argv[0] + " -i directory-of-documents -d dictionary-file -p postings-file"


input_directory = output_file_dictionary = output_file_postings = None

try:
    opts, args = getopt.getopt(sys.argv[1:], 'i:d:p:')
except getopt.GetoptError, err:
    usage()
    sys.exit(2)
    
for o, a in opts:
    if o == '-i': # input directory
        input_directory = a
    elif o == '-d': # dictionary file
        output_file_dictionary = a
    elif o == '-p': # postings file
        output_file_postings = a
    else:
        assert False, "unhandled option"
        
if input_directory == None or output_file_postings == None or output_file_dictionary == None:
    usage()
    sys.exit(2)

csv.field_size_limit(sys.maxsize) # Explain

# Sorted list of docIDs
#documents = sorted(map(int, listdir(input_directory))) # Change those
# Total number of documents
""" 
Given a document with docID N, length[N] stores its length, as described in the lecture
notes, in order to do length normalization.
"""
#length = {docID: 0 for docID in documents} # change this
"""
dictionary is our inverted index, in part 1 & 2 it contains the mapping 
(word: doc_frequency). Part 3 then adds to the value of a (key,value) tupple the 
position of the posting list that corresponds to the key (a word). Hence the final 
mapping is the following: (word: (doc_frequency, offset)).
"""
dictionary = {} 
"""
(word: number) is a bijective mapping, if word is the ith term encountered during the
indexing phase, then number = i. Once the index is complete, number ranges from 0 to 
vocabulary-size-1. This bidirectional dictionary is useful to us, because it can be
used to determine the line in the posting-list-file that corresponds to a given word, 
and vice versa.
"""
word_number = BidirectionalDict() 
vocab_size = 0 # Number of words encountered, grows with the dictionary

postings = []

open(output_file_postings,'w').close() # Create an empty file

#============================= Create the index (Part 1) =============================#
"""
Every file with a docID in documents is opened and read, its words are first processed 
by the nltk tokenizer and second by the stem_and_casefold(word_to_process) function, 
which yields a reduced form of the word.
"""
with open('dataset.csv', 'rb') as csvfile: # Scan all the documents

	law_reports = csv.reader(csvfile, delimiter=',', quotechar='"')
	law_reports.next()
	for rep_nbr, report in enumerate(law_reports):
		if rep_nbr % 1000 == 999:
			print("1000 docs were processed\n")
		docID = int(report[0]) # Extract docID
		#print("Report being processed: " + str(docID))
		content = report[2].decode('UTF8').encode('ASCII',"ignore") # Extract content, encode to ASCII
		words = nltk.word_tokenize(content) # Tokenized words
		#print("First words of the report " + ", ".join(words[:10]) + '\n')
		for word in words:
			reduced_word = stem_and_casefold(word) # Applies stemming and case-folding
			dictionary.setdefault(reduced_word,0)

			if dictionary[reduced_word] == 0: # First occurence of reduced_word
				word_number[reduced_word] = vocab_size 
				new_line = new_node(docID) + '\n' 

				# Append this newly created posting list to posting-list-file
				postings.append(new_line)

				dictionary[reduced_word] += 1 # doc_frequency updated 
				vocab_size += 1 # A new word

			else: # reduced_word already in index
				line_number = word_number[reduced_word] 
				"""
				Using linecache, lines start at 1 (not at 0)
				We need to clear the cache before loading a line, so that it includes
				the most recent changes made to it
				""" 
				line = postings[line_number]
				posting_list = Postings(line)
				last_node = posting_list.value_at(-1) 
				last_docID = get_docID(last_node)

				"""
				If docID and last_docID are identical, we increment the term_frequency
				attribute of last_node. If not, we append a new node to the posting
				list.
				"""
				if  docID == last_docID: # term_frequency needs to be updated
					new_line = posting_list.to_string()[:-NODE_SIZE] + updated_tf(last_node) + '\n'
					postings[line_number] = new_line
				else: # New node appended to the posting list
					new_line = posting_list.to_string() + new_node(docID) + '\n' 
					postings[line_number] = new_line 
					dictionary[reduced_word] += 1 # doc_frequency updated



#============================ Write index to file (Part 2) ===========================#
"""
What remains to be done is to compute the length of every document (square root of the 
sum of tf-idf score squares, computed for all terms in the document), while also 
updating the dictionary with the offset in the posting-list-file that corresponds to a 
certain word. Finally, we serialize both dictionary and length.
"""
with open(output_file_postings, 'w') as outfile_post, open(output_file_dictionary, 'w') as outfile_dict:
	offset = 0

	for i, next_line in enumerate(postings):
		reduced_word = word_number[i]
		next_posting_list = Postings(next_line)

		"""for next_node in next_posting_list: # Iterate over the (docID,term_frequency) pairs
			weight = 1 + math.log10(get_tf(next_node))
			length[get_docID(next_node)] += weight*weight # tf-idf square """

		dictionary[reduced_word] = (dictionary[reduced_word], offset) # Update the dictionary
		outfile_post.write(next_line)
		offset += len(next_line)

	pickle.dump(dictionary,outfile_dict)
	# Final length is obtained after computing the square root of the previous value
	#pickle.dump({docID: math.sqrt(score_acc) for docID, score_acc in length.items()}, outfile_dict) 