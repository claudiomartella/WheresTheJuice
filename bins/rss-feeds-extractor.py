# -*- coding: utf-8 -*-
'''
Created on Apr 6, 2010

@author: hammer
'''

from libs.BeautifulSoup import BeautifulSoup
from urlparse import urljoin
import urllib2, sys, re

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print "should pass the inputfilename"
        sys.exit()
        
    for url in file(sys.argv[1]):
        # ignore comments
        url = url.strip()
        if url[0] == '#':
            continue

        #print "Processing: " + url
        
        html = urllib2.urlopen(url.strip())
        soup = BeautifulSoup(html)
        
        res = soup.findAll('link', rel='alternate', attrs={'type': re.compile("^application/(atom|rss)\+xml")})
        if len(res) == 0:
            #print "Couldn't find the Feed!"
            continue
        
        href = res[0]['href']
        
        # relative link?
        if not href.startswith("http"):
            link = urljoin(url, href)
        else:
            link = href
        
        print link

