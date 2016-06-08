# -*- coding: utf-8 -*-  #한글을 쓸 때는 꼭 붙인다. 
import sys
sys.path.insert(0, 'libs')

import random
import urllib  # URL을 열고 HTML을 읽는 모듈, urllib을 불러온다
import urllib2
from bs4 import BeautifulSoup 

location = u'사당역'
menu = u'한식'
result = []
i = 0
j = 0
    
def getData():
    global result
    tmp = []
    html = urllib.urlopen("http://www.diningcode.com/list.php?query="+location.encode('utf-8')+"+"+menu.encode('utf-8'))
    html = urllib.urlopen("http://www.diningcode.com/list.php?query=사당역+한식")
    soup = BeautifulSoup(html.read(), "html.parser")
 
    list = soup.find_all("div", {"id" : "search_list"})
    index = 0

#     url = 'http://www.diningcode.com/list.php?query=' + location.encode('utf-8') + '+' + menu.encode('utf-8')
#     url = urllib.quote(url,'/:?=&')
#     resp = urllib2.urlopen(url).read()
#     soup = BeautifulSoup(resp,"html.parser")
#     list = soup.find_all('div',{"id" : "search_list"})
#     
#     index = 0

    while index < 3 * 3:
        for restaurants in list:
            name_and_link = restaurants.find_all("a")[index]
            name = name_and_link.text.encode('utf-8')
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
            tmp = []
            print name, link, keyword, address, tel
    
    return result


result = getData()
while (i < 3):
        msg_text = result[i][0].decode('utf-8').encode('utf-8') + result[i][1].decode('utf-8').encode('utf-8')
        print msg_text
        i += 1
