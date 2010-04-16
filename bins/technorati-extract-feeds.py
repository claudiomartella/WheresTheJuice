'''
Created on Apr 10, 2010

@author: hammer
'''

# Known issues:
# 1: some blogs refuse (403) because of user agent

from BeautifulSoup import BeautifulSoup
import urllib2
from urlparse import urljoin
import urllib2, sys, re, socket
import cPickle as pickle

def rssfeedextractor(url):
    html = urllib2.urlopen(url.strip(), timeout=10)
    soup = BeautifulSoup(html)
        
    res = soup.findAll('link', rel='alternate', attrs={'type': re.compile("^application/(atom|rss)\+xml")})
    if len(res) == 0:
        #print "Couldn't find the Feed!"
        return None
        
    href = res[0]['href']
        
    # relative link?
    if not href.startswith("http"):
        link = urljoin(url, href)
    else:
        link = href
        
    return link

# main starts here

numOfPages  = 10
page        = ""
mainpage    = "http://technorati.com/blogs/directory/"
directories = ["entertainment/", "technology/", "business/", "sports/", "politics/", "science/", "living/"]

alldata = {}
socket.setdefaulttimeout(10)

for directory in directories:
    blogs = []
    alldata[directory[:-1]] = blogs
    
    for p in range(2, numOfPages+2):
        try:
            url  = mainpage+directory+page
            html = urllib2.urlopen(url)
            soup = BeautifulSoup(html)
    
            links = soup.findAll('a', attrs={'class': "offsite"})
            print "%s, page %d" % (directory[:-1] , p-1)
            for i in range(0, 10): # 10 links per page
                print links[i]['href']
                blogs.append(links[i]['href'])
                
            page = "page-%d" % p
            
        except Exception as err:
            print "Error parsing %s" % (url)
            print err
            

print "Extracting Feeds"

fout = open("technorati-feeds.txt", "w")

finaldata = {}

for directory, blogs in alldata.iteritems():
    rss = []
    finaldata[directory] = rss
    for blog in blogs:
        try:
            rssurl = rssfeedextractor(blog)
            if not rssurl: continue
            print "%s -> %s" % (blog, rssurl)
            fout.write(rssurl+"\n")
            rss.append(rssurl)
            
        except Exception as err:
            print "Error parsing %s" % (blog)
            print err

fout.close()

pout = open("technorati-rssfeeds.dump", "wb")
pickle.dump(finaldata, pout, protocol=2)
pout.close()
