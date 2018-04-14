#!/usr/bin/python
import re
import nltk
import sys
import getopt
import os
import math

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

#
#Tokenizer
# -in: filename to tokenize
# -out: the tokens of the file
PORTER = nltk.stem.porter.PorterStemmer()
def tokenizeFile(fname):
    f = open(fname,'r')
    text = f.read()
    sentences = nltk.sent_tokenize(text)
    words = []
    for sent in sentences:
        words = words + nltk.word_tokenize(sent)
    tokens = []
    for w in words:
        if not( w == "," or w==".") :
            tokens +=[PORTER.stem(w)]
    f.close()
    return tokens

#
#SPIMI-Invert:
#   Construct the posting list for the given files with the dictionnary
#
# -in: files the files containing the stream of token
# -out:  outs containing the name of the dictionnary file and posting file
def spimiInvert( files , outs):
    dictionary = {}
    dictionary["*"] =[]
    for fname in files:
        fileId = fname.split('/')[-1]
        tokens = tokenizeFile(fname)
        
        lengthVec =0

        for token in tokens:
            
            #if in dictionary then
            #add doc to the posting list if the doc is not already in
            if token in dictionary.keys():
                last = dictionary[token][-1]
                if last[0] != fileId:
                    dictionary[token]+= [(fileId,1)]
                    lengthVec +=1
                else:
                    x = dictionary[token][-1][1]
                    dictionary[token][-1] = (dictionary[token][-1][0],x+1)
                    newW = (1+math.log(x+1,10))
                    oldW = (1+math.log(x,10))
                    lengthVec += newW*newW - oldW*oldW
            
            #if the term is not in the dictionary
            else:
                dictionary[token] = [(fileId,1)]
                lengthVec +=1
            
        # add size of documents
        dictionary["*"] +=[(fileId, math.sqrt(lengthVec))] 
        
    sorted_terms = dictionary.keys()
    sorted_terms.sort()
    # write into a new file
    dicFile = open(outs[0],"w")
    postFile = open(outs[1],"w")
    
    for term in sorted_terms:
        
        # write term and a pointer to the posting list in dictionary
        dicFile.write(term +" "+str(len(dictionary[term]))+" "+ str(postFile.tell())+"\n")
        
        # write the posting list
        for file_id,tf in dictionary[term]:
            postFile.write(file_id+" "+str(tf) +"\n")
    
    dicFile.close()
    postFile.close()

# Read-Term
#  transform a line into a pair term, frequency, pointer
# return a pair: term, pointer
def readTerm(line):
    if line == "":
        return None
    line = line[:-1] #remove \n
    p = line.split()
    p = p[0],int(p[1]),int(p[2])
    return p

# 
#Merge:
# -in: blocks list of files containing blocks informations
# -out: files of the merged dictionnary and posting list
def mergeBlocks( blocks , outs):
    
    # 1) Open files
    dics = []
    posts = []
    mergedDic = open( outs[0],"w")
    mergedPost = open(outs[1],"w")
    for dic,post in blocks:
        dics += [open(dic,"r")]
        posts += [open(post,"r")]
    
    # 2) Initialize
    nbBlocks = len(blocks)
    actualTerms =[]
    nextTerms = []
    for idx in range(nbBlocks):
        line = dics[idx].readline()
        actualTerms += [readTerm(line)]
        line = dics[idx].readline()
        nextTerms += [readTerm(line)]
    
    # 3) merge
    while True:
        termMin = None
        min_ids = []
        
        #identifie the minimum term
        for idx in range(nbBlocks):
            if actualTerms[idx] == None:
                continue
            if actualTerms[idx][0] < termMin or termMin == None:
                termMin = actualTerms[idx][0]
                min_ids = [idx]
            elif actualTerms[idx][0] == termMin :
                min_ids += [idx]
        
        #close if all dictionnary are finished
        if termMin == None:
            break
        #compute total documents frequency
        df = 0
        for i in min_ids:
            df += actualTerms[i][1]
        #write the minimum in the postlist
        mergedDic.write(termMin + " "+str(df)+" "+str(mergedPost.tell()) + "\n" )
        
        #write posting list and update corresponding block
        for i in min_ids:
            #compute the number of bytes to read and seek the position in the file
            posts[i].seek(actualTerms[i][2])
            if nextTerms[i] == None:
                #EOF reached
                postlist = posts[i].read()
            else:
                nbytes = nextTerms[i][2] -actualTerms[i][2]
                postlist = posts[i].read(nbytes)
            #write in the mergedPostinglist
            mergedPost.write(postlist)
            
            #update actual and next term
            actualTerms[i] = nextTerms[i]
            nextTerms[i] = readTerm(dics[i].readline())
    
    # 4) close files
    mergedDic.close()
    mergedPost.close()
    for i in range(nbBlocks):
        dics[i].close()
        posts[i].close()


#--------------------------------CONSTANTS-----------------------------#
DOC_PER_BLOCK = 600
#=================================MAIN=================================#
print("READ FILES")
files = os.listdir(input_directory)
filesInt=[]
for fil in files:
    filesInt +=[int(fil)]
filesInt.sort()
filesSorted = []
for fil in filesInt:
    filesSorted+=[str(fil)]
relativeFiles=[]
for fil in filesSorted:
    relativeFiles+=[input_directory+"/"+fil]
nbFiles = len(files)

#---Index Construction---#
#separate files in block
#call spimi-invert for each block
print("START CONSTRUCTING INDEX")
blocks = []
for i in range(0,nbFiles ,DOC_PER_BLOCK):
    print(str(int(i*100/float(nbFiles)))+"%    BLOCK "+str(i/DOC_PER_BLOCK))
    blockNames = "dic" + str(i/DOC_PER_BLOCK)+".txt", "post" + str(i/DOC_PER_BLOCK)+".txt"
    spimiInvert(relativeFiles[i:i+DOC_PER_BLOCK],blockNames)
    blocks += [blockNames]
print("BLOCKS CREATED\n\nSTART MERGING")
# merge all the blocks in one
mergeBlocks(blocks,(output_file_dictionary,output_file_postings))
print("MERGED")
#delete blocks files
for d,p in blocks :
    os.remove(d)
    os.remove(p)
print("FINISHED")
