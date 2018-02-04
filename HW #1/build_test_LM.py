#!/usr/bin/python
import re
import nltk
import sys
import getopt

languages = ['indonesian','malaysian','tamil'] # A list of the possible languages (could be extended)

def build_LM(in_file):
    """
    build language models for each label
    each line in in_file contains a label and a string separated by a space
    """
    print 'building language models...'
    # This is an empty method
    # Pls implement your code in below
    fh = open(in_file)
    # Keep count of the number of 4-grams encountered, with add-one smoothing
    language_cnt = {language: 0.0 for language in languages} 
    d = {} # Empty dictionary, datastructure to store the mapping (language,4-gram)->count
    for line in fh:
    	label = line.split(' ',1)[0] # label is a language contained in the list languages
    	string = line.split(' ',1)[1] # The actual text, whose language is determined by label
    	if len(string) >= 4: # Check if there is at least one 4-gram
    		for i in range(0,len(string)-3): # Scan through all the 4-grams
    			four_gram = string[i:i+4]
	    		for language in languages:
	    			d.setdefault((language,four_gram),0) 
	    			if d[(language,four_gram)] == 0: # Make sure that there is add-one smoothing
	    				d[(language,four_gram)] += 1
	    				language_cnt[language] += 1 
	    			if language == label:
	    				d[(language,four_gram)] += 1 # New 4-gram encoutered
	    				language_cnt[language] += 1 # Keep the count up to date
    fh.close()
    # Returns a LM, that is a mapping (language,4-gram)->probability
    return {l_fg_tuple: fg_count/language_cnt[l_fg_tuple[0]] for l_fg_tuple, fg_count in d.items()} 
     
def test_LM(in_file, out_file, LM):
    """
    test the language models on new strings
    each line of in_file contains a string
    you should print the most probable label for each string into out_file
    """
    print "testing language models..."
    # This is an empty method
    # Pls implement your code in below
    fi = open(in_file)
    fo = file(out_file, 'w')
    import numpy # Needed for log 
    for line in fi:
    	if len(line) >= 4: # Check if there is at least one 4-gram
    		# Compute log probabilities of the different languages and a given string
    		language_log_prb = {language: 0.0 for language in languages} 
    		stat = ('other',-float('inf')) # Tuple created to track the most likely language
    		for language in languages:
	    		for i in range(0,len(line)-3): # Scan through all the 4-grams
	    			four_gram = line[i:i+4]
	    			# Add log probability, which is 0 if the 4-gram is not in the LM
	    			language_log_prb[language] += numpy.log(LM.get((language,four_gram),1.0)) # Add log probability
	    		# No 4-gram was in the LM (very unlikely: all 4-grams had probability 1)
	    		if language_log_prb[language] == 0.0: 
	    			language_log_prb[language] = -float('inf') 
	    		if language_log_prb[language] > stat[1]: # Update stat
	    			stat = (language,language_log_prb[language])
	    	fo.write(stat[0] + ' ' + line)
    fi.close()
    fo.close()

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
