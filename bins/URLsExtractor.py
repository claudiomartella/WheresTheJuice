'''
Created on Apr 12, 2010

@author: hammer
'''

import feedparser, urllib2, re, psyco
import htmlentitydefs
import BeautifulSoup

psyco.full()

class URLsExtractor:
    _rss = None
    
    def _get_content_from_url(self, url):
        page = urllib2.urlopen(url, timeout=10)
        soup = BeautifulSoup.BeautifulSoup(page,convertEntities=BeautifulSoup.BeautifulStoneSoup.HTML_ENTITIES)

        # ignore comments
        comments = soup.findAll(text=lambda text:isinstance(text,BeautifulSoup.Comment))
        [comment.extract() for comment in comments]
        # ignore scripts
        scripts  = soup.findAll('script')
        [script.extract() for script in scripts]
        # ignore styles
        styles = soup.findAll('style')
        [style.extract() for style in styles]
        
        body = soup.body(text=True)
        return  ' '.join(body)
        
    def _strip_html(self, text):
        def fixup(m):
            text = m.group(0)
            if text[:1] == "<":
                return "" # ignore tags
            if text[:2] == "&#":
                try:
                    if text[:3] == "&#x":
                        return unichr(int(text[3:-1], 16))
                    else:
                        return unichr(int(text[2:-1]))
                except ValueError:
                    pass
            elif text[:1] == "&":
                entity = htmlentitydefs.entitydefs.get(text[1:-1])
                if entity:
                    if entity[:2] == "&#":
                        try:
                            return unichr(int(entity[2:-1]))
                        except ValueError:
                            pass
                    else:
                        return unicode(entity, "iso-8859-1")
            return text # leave as is
        return re.sub("(?s)<[^>]*>|&#?\w+;", fixup, text)
       
    def __init__(self, rss):
        self._rss = rss
        
    def get_posts(self, real=False):
        posts = []
        
        try:
            d = feedparser.parse(self._rss)
        
        except Exception as err:
            print "Error parsing rss %s" % (self._rss)
            print err.msg
            return posts
        
        for post in d.entries:
            item = {}
            try:
                item['title'] = self._strip_html(post.title)
                item['link']  = post.link
    
                # go get the actual content from the original post page
                if real == True:
                    item['content'] = self._get_content_from_url(post.link)
                else:
                    if "content" in post:
                        item['content'] = self._strip_html(" ".join(content['value'] for content in post.content))
                    elif "summary" in post: 
                        item['content'] = self._strip_html(post.summary)
                    elif "description" in post:
                        item['content'] = self._strip_html(post.description)
                    else:
                        item['content'] = item['title']
                
                posts.append(item)
                
            except Exception as err:
                print err.msg
                pass # ignore un-parsable posts

        return posts
