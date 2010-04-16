'''
Created on Apr 12, 2010

@author: hammer
'''
import feedparser, sys
import urllib2, urlparse
from BeautifulSoup import BeautifulSoup
from URLsExtractor import URLsExtractor

blogsearchurl = "http://blogsearch.google.com/blogsearch_feeds?hl=en&q=%s&ie=utf-8&num=%d&output=rss"

def getblogsearchurl(tag):
    return blogsearchurl % (tag, 100)

posts = {}

if len(sys.argv) != 2:
    print "should pass the tags to search"
    sys.exit()

for tag in sys.argv[1].split():
    url  = getblogsearchurl(tag)
    posts = URLsExtractor(url).get_posts(real=True)
    
    for post in posts:
        print post['link']
        print post['title'].encode('ascii', 'ignore')
        print post['content'].encode('ascii', 'ignore')[:500]
    