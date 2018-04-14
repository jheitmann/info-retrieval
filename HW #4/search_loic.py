#!/usr/bin/python
import re
import nltk
import sys
import getopt
import os

def usage():
    print "usage: " + sys.argv[0] + " -d dictionary-file -p postings-file -q file-of-queries -o output-file-of-results"

dictionary_file = postings_file = file_of_queries = output_file_of_results = None

try:
    opts, args = getopt.getopt(sys.argv[1:], 'd:p:q:o:')
except getopt.GetoptError, err:
    usage()
    sys.exit(2)

for o, a in opts:
    if o == '-d':
        dictionary_file  = a
    elif o == '-p':
        postings_file = a
    elif o == '-q':
        file_of_queries = a
    elif o == '-o':
        file_of_output = a
    else:
        assert False, "unhandled option"

if dictionary_file == None or postings_file == None or file_of_queries == None or file_of_output == None :
    usage()
    sys.exit(2)

#------------------------GLOBAL VARIABLES------------------------------#

posts = open(postings_file,"r")
dic = open(dictionary_file,"r")
dicSize = os.path.getsize(dictionary_file)
PORTER = nltk.stem.porter.PorterStemmer()

#----------------------------------------------------------------------#

#---------------------------PARSING METHOD-----------------------------#

#Regroup the query so it can be interpreted
def regroup( query):
    newQuery = []
    
    #Parenthesis
    
    while query:
        el = query.pop(0)
        if el == "(":
            group,rest = regroup(query)
            newQuery += [group]
            query = rest
        elif el == ")":
            break
        else:
            newQuery += [el]
    #NOT
    newQuery2 = []
    
    while newQuery:
        el = newQuery.pop(0)
        if el == "NOT":
            newQuery2 += [("NOT",newQuery.pop(0))]
        else:
            newQuery2 += [el]
        
    #AND
    newQuery3 = []
    while newQuery2:
        el = newQuery2.pop(0)
        if el == "AND":
            newQuery3 += [("AND",newQuery3.pop(),newQuery2.pop(0))]
        else:
            newQuery3 += [el]
        
    #OR
    newQuery4 = []
    while newQuery3:
        el = newQuery3.pop(0)
        if el == "OR":
            newQuery4 += [("OR",newQuery4.pop(),newQuery3.pop(0))]
        else:
            newQuery4 += [el]
    
    return newQuery4 , query
#----------------------------------------------------------------------#

#----------------------------------------------------------------------#





#------------------------------LISTS METHODS---------------------------#

#STRUCTURE:
#if in memory:
#   list = (el, list)
#if in Hard Drive:
#   list = (el, pointer to next, skip pointer , end pointer)


def createList(list1):
    if isinstance(list1,list):
        if list1:
            return (list1.pop(0),list1)
        else:
            return None
    else:
        posts.seek(list1[0])
        nextLine=posts.readline()
        nextLine = nextLine[:-1].split(":")
        if len(nextLine) == 1:
            return (int(nextLine[0]),posts.tell(),None,list1[1])
        else:
            return (int(nextLine[0]),posts.tell(),posts.tell()+int(nextLine[1]),list1[1])

def nextEl(el):
    if isinstance(el[1], list):
        if el[1]:
            return (el[1].pop(0),el[1])
        else:
            return None
    else:
        posts.seek(el[1])
        nextLine=posts.readline()
        if el[3] == -1:
            if nextLine =="":
                return None
        elif el[3] <= el[1]:
            return None
        nextLine = nextLine[:-1].split(":")
        if len(nextLine) == 1:
            return (int(nextLine[0]),posts.tell(),None,el[3])
        else:
            return (int(nextLine[0]),posts.tell(),posts.tell()+int(nextLine[1]),el[3])

def hasSkip(el):
    if isinstance(el[1], list):
        return False
    else:
        return el[2] != None
        
def skip(el):
    el,ptr,skipPtr,end = el
    posts.seek(skipPtr)
    nextLine=posts.readline()
    nextLine = nextLine[:-1].split(":")
    if len(nextLine) == 1:
        return (int(nextLine[0]),posts.tell(),None,end)
    else:
        return (int(nextLine[0]),posts.tell(),posts.tell()+int(nextLine[1]),end)


#----------------------------------------------------------------------#


#------------------------COMBINATIONS METHODS--------------------------#

#FIND POST:
#   find the pointer to the posting list
def findPost(query):
    if query == "*":
        dic.seek(0)
        a = dic.readline()
        term,ptr = a.split()
        a= dic.readline()
        nextTerm,end = a.split()
        return long(ptr),long(end)
    
    
    query = PORTER.stem(query)
    dic.seek(0)
    dic.readline() #skip whole dictionnary
    lower = dic.tell()
    higher = dicSize
    mid=0
    while higher-lower >40:#threshold
        dic.seek((higher+lower)/2)
        a= dic.readline()
        mid = dic.tell()
        a = dic.readline()
        term,ptr = a.split()
        if term==query:
            nextLine = dic.readline()
            if nextLine != "":
                nextTerm,end = nextLine.split()
            else:
                end = "-1"
            return long(ptr),long(end)
        elif term < query:
            lower = mid
        else:
            higher = mid
    
    dic.seek(lower)
    while dic.tell()<higher:
        a=dic.readline()
        term,ptr = a.split()
        if term==query:
            nextLine = dic.readline()
            if nextLine != "":
                nextTerm,end = nextLine.split()
            else:
                end = "-1"
            return long(ptr),long(end)
        elif term > query:
            return []
            
    return []
    
    
    
#COMBINE LIST WITH "OR":
#   merge the result of both list in one
def combineOr((n1,list1),(n2,list2)):
    #since A or !B == !( !A and B) we simply use this information
    if n1 or n2:
        negation ,result = intersectWithSkip((not n1,list1),(not n2,list2))
        return (not negation,result)
    else:
        p1= createList(list1)
        p2=createList(list2)
        answer = []
        while p1!= None and p2 != None:
            if p1 == None:
                answer += [p2[0]]
                p2=nextEl(p2)
            elif p2==None:
                answer += [p1[0]]
                p1=nextEl(p1)
            elif p1[0] == p2[0]:
                answer += [p1[0]]
                p1 = nextEl(p1)
                p2=nextEl(p2)
            elif p1[0] < p2[0]:
                answer += [p1[0]]
                p1=nextEl(p1)
            else:
                answer += [p2[0]]
                p2= nextEl(p2)
        return (False,answer)

#INTERSECT LIST WITH "AND":
#   use known algorithm to intersect 2 lists using skip pointers
#
def intersectWithSkip((n1,list1),(n2,list2)):
    
    if n1 and n2:
        negation, result = combineOr((not n1,list1),(not n2,list2))
        return (not negation,result)
    else:
        if n1:
            p1=createList(list2)
            p2 = createList(list1)
            n2 = n1
            n1 = False
        else:
            p1 = createList(list1)
            p2= createList(list2)
        answer = []
        while p1!=None:
            if p2 == None:
                if n2:
                    answer += [p1[0]]
                    p1 = nextEl(p1)
                else:
                    p1 = None
            elif p2[0] == p1[0]:
                if not n2:
                    answer += [p1[0]]
                p1 = nextEl(p1)
                p2 = nextEl(p2)
            elif p1[0]<p2[0]:
                if not n2 and hasSkip(p1):
                    sk = skip(p1)
                    while hasSkip(p1) and sk[0] <=p2[0]:
                        p1 = sk
                        if hasSkip(p1):
                            sk = skip(p1)
                if p1[0]<p2[0]:
                    if n2:
                        answer += [p1[0]]
                    p1 = nextEl(p1)
            else:
                if hasSkip(p2):
                    sk = skip(p2)
                    while hasSkip(p2) and sk[0] <=p1[0]:
                        p2 = sk
                        if hasSkip(p2):
                            sk = skip(p2)
                if p2[0] < p1[0]:
                    p2 = nextEl(p2)
        return (False,answer)
        
        
def loadPostingList((ptr,end)):
    posts.seek(ptr)
    if end == -1:
        postingStr = posts.read()
    else:
        postingStr = posts.read(end-ptr)
    postList = postingStr.split("\n")
    postList.pop()
    final = []
    for el in postList:
        el=el.split(":")
        final+=[int(el[0])]
    return final
    
#----------------------------------------------------------------------#


#---------------------------RECURSIVE EVALUATION-----------------------#
#EVALUATE:
#   evaluate the result of the query using recursion
#   -in: the parsed/grouped query to evaluate
#   -return: a pair (NOT,result) where Not is the negation and result is the result list
def evaluate(query):
    #if we reached a leaf of the query, we find the corresponding posting List
    if isinstance(query,basestring):
        return (False,findPost(query))
    
    elif query[0] == "OR":
        return combineOr(evaluate(query[1]),evaluate(query[2]))
    elif query[0] == "NOT":
        res = evaluate(query[1])
        return (not res[0],res[1])
    elif query[0] == "AND":
        return intersectWithSkip(evaluate(query[1]),evaluate(query[2]))
    elif len(query) == 1:
        return evaluate(query[0])
    else:
        return (False, ["ERROR"])



def evaluateRoot(query):
    negation, result = evaluate(query)
    if isinstance(result,tuple):
        result =loadPostingList(result)
    if negation:
        negation,result =intersectWithSkip((False,findPost("*")),(negation,result))
    output=""
    for docId in result:
        output += str(docId) + " "
    return output


#----------------------------------------------------------------------#

#==============================MAIN====================================#

queries = open(file_of_queries,"r")
results = open(file_of_output,"w")

for query in queries:
    #split and add space
    query = query.replace("("," ( ").replace(")"," ) ").split()

    
    #interprete the query
    query,rest = regroup(query)
    if rest:
        assert False, "Wrong parenthesis"
    
    #evaluate the result and write it
    result= evaluateRoot(query)
    results.write(result + "\n")

posts.close()
dic.close()
queries.close()
results.close()

