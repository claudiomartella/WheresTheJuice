'''
Created on Apr 13, 2010

@author: hammer
'''

from URLsExtractor import URLsExtractor
from operator import itemgetter
import cPickle as pickle
import networkx as nx
import re, nltk, psyco

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

def calculate_frequencies(words, freqs, condfreqs):
    for word in words:
        freqs.inc(word)
        for otherword in words:
            if otherword != word:
                condfreqs[word].inc(otherword)


def extract_POS_bag(text, stopwords):
    words = []
    #tokens=re.compile(r'[^A-Z^a-z]+').split(text)
    tokens=nltk.wordpunct_tokenize(text)
    taggs=nltk.pos_tag(tokens)
    
    for word, tag in taggs:
        # ignore non-words
        word = word.lower()
        if word in stopwords or word == '': continue
        
        if tag == 'NNP': # accept named entities
            words.append(word)
        elif tag == 'NN' or tag == 'NNS': # accept nouns and stem them
            words.append(stemmer.stem(word))
        else: # ignore verbs, adverb, adjectives etc.
            continue
    
    return words

def get_POS_keywords(words, number=15):
    keywords = []
    
    if len(words) == 0: return []
    
    g  = create_graph(words)
    pr = nx.pagerank(g, alpha=0.9, tol=0.001)
    
    keyset = set(dict(sorted(pr.iteritems(), key=itemgetter(1), reverse=True)[0:number]).keys())
    
    return keyset    

def print_trends(trend_freqs, trend_cfreq):
    for directory, frequency in trends_freqs.iteritems():
        topNwords = frequency.sorted()[:100]
        print "For directory: " % (directory)
        for word in topNwords:
            print "\t%s" % (word)
            for coword in trends_cfreq[directory].sorted()[:25]:
                if coword in topNwords:
                    print "\t\t*** %s ***" % (coword)
                else:
                    print "\t\t%s" % (coword)

# MAIN starts here    

psyco.full()    

stopwords = set([line.strip() for line in file('stopwords.txt')])

trends_freqs     = {}
trends_condfreqs = {}

try:
    pin = open("technorati-rssfeeds.dump", "rb")
    dictionary = pickle.load(pin)
    pin.close()
except Exception as err:
    print "Error loading technorati's seeds file"
    print err
    
for directory, blogs in dictionary.iteritems():
    freqs     = nltk.probability.FreqDist()
    condfreqs = nltk.probability.ConditionalFreqDist()
    trends_freqs[directory]     = freqs
    trends_condfreqs[directory] = condfreqs
    
    num_of_blogs = len(blogs)
    
    for i, blog in enumerate(blogs):
        extractor = URLsExtractor(blog)
        try:
            posts = extractor.get_posts()
        except Exception as err:
            print "Error parsing: %s" % (blog)
            continue
        
        for post in posts:
            print "%s (%d/%d): Analyzing %s" % (directory, i+1, num_of_blogs, post['link'])
            bag_of_words = extract_POS_bag(post['title'] + " " + post['content'], stopwords)
            keywords = get_POS_keywords(bag_of_words)
            #print keywords
            calculate_frequencies(keywords, freqs, condfreqs)
    
print_trends(trend_freqs, trend_cfreq)
            
#trends_freqs  = open("trends_freqs.dump", "wb")
#trends_cfreqs = open("trends_cfreqs.dump", "wb")
#pickle.dump(trends_freqs, trends_freqs, protocol=2)
#pickle.dump(trends_condfreqs, trends_cfreqs, protocol=2)
#trends_freqs.close()
#trends_cfreqs.close()