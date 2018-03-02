#!/usr/bin/python
import re
import nltk
import sys
import getopt
import linecache
try:
   import cPickle as pickle
except:
   import pickle
from tools import tokenize
from tools import Root
from tools import Element

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

NUMBER_OF_DOCS = 10 # Number of documents in the directory directory-of-documents, total = 14818

index = {} # Inverted index
vocab_size = 0

with open(output_file_dictionary, 'w') as outfile_dict, open(output_file_postings, 'r+', encoding='utf-8') as outfile_post:
	# Create the index (Part 1)
	for doc in range(1, number_of_docs+1):
		doc_path = input_directory + str(doc)
		with open(doc_path, 'r') as next_doc:
			for line in next_doc:
				words = line.split(' ')
				for word in words:
					tokenized_word = tokenize(word)
					index.setdefault(tokenized_word, (vocab_size, 0, 777)) # 777 should be replaced by offset...
					if index[tokenized_word][1] == 0 :
						new_line = pickle.dumps(Root(doc)) + '\n' # Serializes a new root, containing doc
						outfile_post.seek(0,2) # 2: we want to append the new words posting list
						outfile_post.write(new_line)
						index[tokenized_word][1] += 1 # First occurence 
						vocab_size += 1 
					else:
						"""
						linecache loads the nth line of outfile_post into cache, where n is index[tokenized_word]
						This line is a serialized linked list, pickle.loads deserializes the line and saves it as 
						posting_list
						"""
						line_number = index[tokenized_word][0]
						posting_list = pickle.loads(linecache.getline(outfile_post, line_number)) # Cache -> clear
						if posting_list.last.docID != doc:
							posting_list.append_element(Element(doc))
							new_line = pickle.dumps(posting_list) + '\n'
							# Need to overwrite the whole file
							index[tokenized_word][1] += 1
	# Add Skip pointers (Part 2)




						
					



