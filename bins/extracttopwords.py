#!/usr/bin/env python 

import feedparser
import re
import networkx as nx
import nltk
import urllib
import sys
import codecs
from operator import itemgetter

stemmer = nltk.stem.PorterStemmer()

def calculate_indices(pivot, documentSize, windowSize):
    left = pivot - (windowSize/2)
    if left < 0: left = 0
    right = pivot + (windowSize/2) + 1
    if right > documentSize: right = documentSize
    
    return (left, right)
    
def create_graph(document):
    g = nx.DiGraph()
    
    documentSize = len(document)
    
    for i, pivot in enumerate(document):
        (left, right) = calculate_indices(i, documentSize, 5)
        window = document[left:right]
        
        g.add_node(pivot)
        for word in window:
            if word == pivot: pass
            g.add_node(word)
            g.add_edge(pivot, word)
    
    return g

def countwords(text, keywords):
    wordcounts = {}
    
    for word in text:
        if word in keywords:
            wordcounts.setdefault(word, 0)
            wordcounts[word] += 1

    return wordcounts

def getPOSwords(html, stopwords):
    words = []
    txt=re.compile(r'<[^>]+>').sub('',html)
    #tokens=nltk.word_tokenize(txt)
    tokens=re.compile(r'[^A-Z^a-z]+').split(txt)
    taggs=nltk.pos_tag(tokens)
    
    for word, tag in taggs:
        # ignore non-words
        word = word.lower()
        if word in stopwords: continue
        
        if tag == 'NNP':
            words.append(word)
        elif tag == 'NN':
            words.append(stemmer.stem(word))
        else:
            continue
    
    return words

def getPOSkeywords(url, stopwords, number=50):
    keywords = {}
    d = feedparser.parse(url)
    
    for e in d.entries:
        if 'summary' in e: summary = e.summary
        else: summary = e.description
    
        words = getPOSwords(e.title + ' ' + summary, stopwords)
        g     = create_graph(words)
        pr    = nx.pagerank(g, alpha=0.9, tol=0.001)
    
        keyset = set(dict(sorted(pr.iteritems(), key=itemgetter(1), reverse=True)[0:number]).keys())
        keywords[urllib.quote(e.link, safe='')] = countwords(words, keyset)

        print e.link
    
    return keywords    

def getwords(html, stopwords):
  # Remove all the HTML tags
  txt=re.compile(r'<[^>]+>').sub('',html)

  # Split words by all non-alpha characters
  words=re.compile(r'[^A-Z^a-z]+').split(txt)
  words=[word.lower() for word in words]
  
  # Convert to lowercase
  return [word for word in words if word!='' and word not in stopwords]

def getkeywords(url, stowords, number=50):
    keywords = {}
    d = feedparser.parse(url)
    
    for e in d.entries:
        if 'summary' in e: summary = e.summary
        else: summary = e.description
    
        words = getwords(e.title + ' ' + summary, stopwords)
        g     = create_graph(words)
        pr    = nx.pagerank(g, alpha=0.9, tol=0.001)
    
        keyset = set(dict(sorted(pr.iteritems(), key=itemgetter(1), reverse=True)[0:number]).keys())
        keywords[urllib.quote(e.link, safe='')] = countwords(words, keyset)

        print e.link
    
    return keywords

# MAIN BEGINS HERE

if len(sys.argv) != 2:
    print "should pass the rssfeeds file"
    sys.exit()

apcount = {}
wordcounts = {}
feedlist  = [line for line in file(sys.argv[1])]
stopwords = set([line.strip() for line in file('stopwords.txt')])

totalposts = 0

for feedurl in feedlist:
    try:
        RSSentries = getPOSkeywords(feedurl, stopwords)
        totalposts += len(RSSentries)
        for name, post in RSSentries.items():
            wordcounts[name] = post
            for word, count in post.items():
                apcount.setdefault(word, 0)
                if count > 1:
                    apcount[word] += 1

    except Exception as err:
        print "Failed to parse %s" % feedurl
        print err

wordlist = []

for word, counts in apcount.items():
    frac = float(counts)/totalposts
    #if frac > 0.1:
    wordlist.append(word)
    print "%s: %f" % (word, frac)

out = codecs.open('blogdata.txt','w', 'utf-8')
out.write('Post')
for word in wordlist: out.write('\t%s' % word)
out.write('\n')
for blog, wc in wordcounts.items():
    print blog
    out.write(blog)
    for word in wordlist:
        if word in wc: out.write('\t%d' % wc[word])
        else: out.write('\t0')
    out.write('\n')

out.close()