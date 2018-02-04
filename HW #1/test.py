languages = ['indonesian','malaysian','tamil'] # A list of the possible languages (could be extended)

"""
build language models for each label
each line in in_file contains a label and a string separated by a space
"""
print 'building language models...'
# This is an empty method
# Pls implement your code in below
fh = open('input.train.txt')
language_cnt = {language: 0.0 for language in languages} # Keep count of the number of 4-grams encountered, with add-one smoothing
d = {} # Empty dictionary, datastructure to store the mapping (language,four_gram)->count
for line in fh:
	prefix = line.split(' ', 1)[0] # prefix is a language contained in the list languages
	tail = line.split(' ', 1)[1] # The actual text, whose language is determined by prefix
	if len(tail) >= 4: # Check if there is at least one 4-gram
		for i in range(0,len(tail)-3): # Scan through all the 4-grams
			four_gram = tail[i:i+4]
	    		for language in languages:
	    			d.setdefault((language,four_gram),0) 
	    			if d[(language,four_gram)] == 0: # Make sure that there is add-one smoothing
	    				d[(language,four_gram)] += 1
	    				language_cnt[language] += 1 
	    			if language == prefix:
	    				d[(language,four_gram)] += 1 # New 4-gram encoutered
	    				language_cnt[language] += 1 # Keep the count up to date
fh.close()
test_d = {language: 0.0 for language in languages}
for l_fg_tuple, count in d.items():
	test_d[l_fg_tuple[0]] += count
print language_cnt
print test_d


"""
string = 'Oel hu Txew trram na\'rngit tarmok, tsole\'a syeptutet atsawl frato m srey.'
ls = [string[i:i+4] for i in range(0,len(string)-3)]

f = open('input.train.txt')
for line in f:
	language = line.split(' ',1)[0]
	text = line.split(' ',1)[1]
	for i in range(0,len(text)-3):
		four_gram = text[i:i+4]
		if four_gram in ls:
			print four_gram + ' ---> ' + line
print string
print 'DONE'
"""
