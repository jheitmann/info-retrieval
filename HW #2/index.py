#!/usr/bin/python
import re
import nltk
import sys
import getopt

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

NUMBER_OF_DOCS = 14818 # Number of documents in the directory directory-of-documents

with open(output_file_dictionary, 'w') as outfile_dict, open(output_file_postings, 'r+', encoding='utf-8') as outfile_post:
	for i in range(1, number_of_docs+1):
		doc_path = input_directory + str(i)
		with open(doc_path, 'r') as next_doc:
			
