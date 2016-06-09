# -*- coding: utf-8 -*-  #한글을 쓸 때는 꼭 붙인다.
import sys
# from chardet.test import result
sys.path.insert(0, 'libs')
# reload(sys)
# sys.setdefaultencoding('utf8')
# 
# from google.appengine.api import urlfetch
# from google.appengine.ext import ndb
from bs4 import BeautifulSoup
# import webapp2
import urllib2
import urllib

result = []
location = '사당역'
menu = '회'
count = 10
# class MainHandler(webapp2.RequestHandler):
#     def get(self):
def getData():
    result = []
    global location, menu
    
    html = urllib2.urlopen('http://www.diningcode.com/list.php?query=' + location + '+' + menu)
    soup = BeautifulSoup(html.read(), "html.parser")
    
    list = soup.find_all("div", {"id" : "search_list"})
    index = 0
    
    while index < count * 3:
        for restaurants in list:
            tmp = []
            name_and_link = restaurants.find_all('a')[index]
            name = name_and_link.text.encode('utf-8').replace(' ','')
            link = "http://www.diningcode.com/" + name_and_link["href"].split("&")[0]
            
            info = restaurants.find_all("div", {"class" : "dc-restaurant-info"})
            keyword = info[index].text.encode('utf-8').replace('\n', '')
            address = info[index + 1].text.encode('utf-8').replace('\n', '')
            tel = info[index + 2].text.encode('utf-8').replace('\n', '')
            index = index + 3
                
            tmp.append(name)
            tmp.append(link)
            tmp.append(keyword)
            tmp.append(address)
            tmp.append(tel)            
            result.append(tmp)
    return result        
#         self.response.write(result)


# app = webapp2.WSGIApplication([
#                                ('/', MainHandler)
#                                ], debug=True)

result = getData()
for restaurant in result:
    print '"' + "('" + location + "'" + ", '"+ menu+"', '" + restaurant[0].decode('utf-8').encode('utf-8') + "'" + ", '" + restaurant[1].decode('utf-8').encode('utf-8') + "'" + ", '" + restaurant[3].decode('utf-8').encode('utf-8')+ "'" + ", '" + restaurant[4].decode('utf-8').encode('utf-8') +"'),"+'"'+"+"