#-*- coding: utf-8 -*-  #한글을 쓸 때는 꼭 붙인다. 문자 인코딩을 UTF-8로 하겠다는 것이다. 인코딩은 앞으로 계속 속썩일 것이다.

import urllib #URL을 열고 HTML을 읽는 모듈, urllib을 불러온다
from bs4 import BeautifulSoup 

def getData(location, menu):
    html = urllib.urlopen("http://www.diningcode.com/list.php?query="+location+"+"+menu)
    soup = BeautifulSoup(html.read(), "html.parser")

    list = soup.find_all("div", {"id" : "search_list"})
    index = 0

    while index < 30 * 3:
        for restaurants in list:
            name_and_link = restaurants.find_all("a")[index]
            name = name_and_link.text.encode('utf-8')
            link = "http://www.diningcode.com/" + name_and_link["href"].split("&")[0]
    
            info = restaurants.find_all("div", {"class" : "dc-restaurant-info"})
            keyword = info[index].text.encode('utf-8').replace('\n', '')
            address = info[index+1].text.encode('utf-8').replace('\n', '')
            tel = info[index+2].text.encode('utf-8').replace('\n', '')
            index = index + 3
    
            print name, link, keyword, address, tel
            result = name + link + keyword + address + tel
    
    return result