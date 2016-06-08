# -*- coding: utf-8 -*-  #한글을 쓸 때는 꼭 붙인다.
import sys
sys.path.insert(0, 'libs')
reload(sys)
sys.setdefaultencoding('utf8')

from google.appengine.api import urlfetch
from google.appengine.ext import ndb
from bs4 import BeautifulSoup
import webapp2
import urllib2
import urllib

class MainHandler(webapp2.RequestHandler):
    def get(self):
        html = urllib2.urlopen('http://www.diningcode.com/list.php?query=사당역+한식')
        soup = BeautifulSoup(html.read(), "html.parser")
        
        list = soup.find_all("div", {"id" : "search_list"})
        index = 0
        
        while index < 10 * 3:
            for restaurants in list:
                name_and_link = restaurants.find_all('a')[index]
                name = name_and_link.text.encode('utf-8')
                link = "http://www.diningcode.com/" + name_and_link["href"].split("&")[0]
                
                info = restaurants.find_all("div", {"class" : "dc-restaurant-info"})
                keyword = info[index].text.encode('utf-8').replace('\n', '')
                address = info[index + 1].text.encode('utf-8').replace('\n', '')
                tel = info[index + 2].text.encode('utf-8').replace('\n', '')
                index = index + 3
                    
                result = [name, link, keyword, address, tel]
            self.response.write(result)


app = webapp2.WSGIApplication([
                               ('/', MainHandler)
                               ], debug=True)
