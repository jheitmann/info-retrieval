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
