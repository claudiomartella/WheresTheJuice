'''
Created on Apr 10, 2010

@author: hammer
'''
import urllib2
from BeautifulSoup import BeautifulSoup

class RSSFeedExtractor(object):
    __link = None
    
    def getFeedURL(self):
        return self.__link

    def __init__(self, url):
        html = urllib2.urlopen(url.strip())
        soup = BeautifulSoup(html)
        
        res = soup.findAll('link', rel='alternate', attrs={'type': re.compile("^application/(atom|rss)\+xml")})
        if len(res) == 0:
            #print "Couldn't find the Feed!"
            continue
        
        href = res[0]['href']
        
        # relative link?
        if not href.startswith("http"):
            self.__link = urljoin(url, href)
        else:
            self.__link = href