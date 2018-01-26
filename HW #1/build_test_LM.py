#!/usr/bin/python
import re
import nltk
import sys
import getopt

def build_LM(in_file):
    """
    build language models for each label
    each line in in_file contains a label and a string separated by a space
    """
    print 'building language models...'
    # This is an empty method
    # Pls implement your code in below
    fh = open(in_file)
    languages = {'indonesian': 0,'malaysian': 0,'tamil': 0}
    d = {}
    for line in fh:
    	prefix = line.split(' ', 1)[0]
    	tail = line.split(' ', 1)[1]
    	if len(tail) >= 4:
    		for i in range(0,len(tail)-3):
    			four_gram = tail[i:i+4]
	    		for language in languages.keys():
	    			d.setdefault((language,four_gram),1)
	    			if language == prefix:
	    				d[(language,four_gram)] += 1
	    				languages[language] += 1
	    			elif d[(language,four_gram)] == 1:
	    				languages[language] += 1
    fh.close()
    return {(language,four_gram): d[(language,four_gram)]/languages[language] for language, four_gram in d.keys()}
    
def test_LM(in_file, out_file, LM):
    """
    test the language models on new strings
    each line of in_file contains a string
    you should print the most probable label for each string into out_file
    """
    print "testing language models..."
    # This is an empty method
    # Pls implement your code in below

def usage():
    print "usage: " + sys.argv[0] + " -b input-file-for-building-LM -t input-file-for-testing-LM -o output-file"

input_file_b = input_file_t = output_file = None
try:
    opts, args = getopt.getopt(sys.argv[1:], 'b:t:o:')
except getopt.GetoptError, err:
    usage()
    sys.exit(2)
for o, a in opts:
    if o == '-b':
        input_file_b = a
    elif o == '-t':
        input_file_t = a
    elif o == '-o':
        output_file = a
    else:
        assert False, "unhandled option"
if input_file_b == None or input_file_t == None or output_file == None:
    usage()
    sys.exit(2)

LM = build_LM(input_file_b)
test_LM(input_file_t, output_file, LM)
