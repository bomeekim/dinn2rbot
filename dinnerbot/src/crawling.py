#-*- coding: utf-8 -*-  #한글을 쓸 때는 꼭 붙인다. 문자 인코딩을 UTF-8로 하겠다는 것이다. 인코딩은 앞으로 계속 속썩일 것이다.

import urllib #URL을 열고 HTML을 읽는 모듈, urllib을 불러온다
from bs4 import BeautifulSoup 


# html = urllib.urlopen("http://movie.naver.com/movie/running/current.nhn?view=list&tab=normal&order=reserve")
# soup = BeautifulSoup(html.read(), "html.parser")
# # 영화 제목이 페이지에 dt로 class 명이 tit로 되어 있기 때문이다.
# data = soup.findAll("dt", { "class" : "tit" })
# # 아래의 과정은 제목만 뽑아 내기 위함
# data = str(data)
# data = data.split("<")
# for i in range(len(data)):
#     if i % 5 == 2:
#         print data[i].split(">")[1]


html = urllib.urlopen("http://www.diningcode.com/pop_list.php")
soup = BeautifulSoup(html.read(), "html.parser")

list = soup.find_all("div", {"id" : "pop_search_list"})

for i in list:
    print i.get_text().encode('utf-8')

for link in soup.find_all('a') :
    print link.get('href')