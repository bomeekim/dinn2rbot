# -*- coding: utf-8 -*-
#


import sys
sys.path.insert(0, 'libs')
reload(sys)
sys.setdefaultencoding('utf8')

import os

# 구글 앱 엔진 라이브러리 로드
from google.appengine.api import urlfetch
from google.appengine.ext import ndb
import webapp2

# URL, JSON, 로그, 정규표현식 관련 라이브러리 로드
import urllib
import urllib2
import json
import logging
import re 

# 메뉴 아무거나
import random

# 크롤링
from bs4 import BeautifulSoup 
import MySQLdb
# 봇 토큰, 봇 API 주소
TOKEN = '222474870:AAFJkDwrJ0BnqQI3IKwRr4S0PDf89brjJQE'
BASE_URL = 'https://api.telegram.org/bot' + TOKEN + '/'

# 봇이 응답할 명령어
CMD_START = '/start'
CMD_STOP = '/stop'
CMD_HELP = '/help'
CMD_BROADCAST = '/broadcast'
CMD_TODAY = '/today'
CMD_TV = '/tv'

# 전역변수
process = 0
menu = u'한식'
menu_detail = ''
location = u'사당'
cid = 0

# Random Menu 거부용 전역변수
rejectMenu = []
nowNumber = -1

# MySQL 변수
CLOUDSQL_PROJECT = 'dinnerbot-1326'
CLOUDSQL_INSTANCE = 'category'

# 봇 사용법 & 메시지
USAGE = u"""[사용법] 아래 명령어를 메시지로 보내거나 버튼을 누르시면 됩니다.
/start - (봇 활성화)
/stop  - (봇 비활성화)
/help  - (이 도움말 보여주기)
"""
MSG_START = u'안녕하세요. 맛집찾기의 달인 최비서입니다.^_^\n현재 계신 곳의 위치 또는 식사할 위치를 알려주세요.'
MSG_STOP = u'감사합니다. 언제든지 불러만 주세요~'

# 커스텀 키보드
CUSTOM_KEYBOARD = [
        [CMD_START],
        [CMD_STOP],
        [CMD_HELP]
        ]

# 채팅별 봇 활성화 상태
# 구글 앱 엔진의 Datastore(NDB)에 상태를 저장하고 읽음
# 사용자가 /start 누르면 활성화
# 사용자가 /stop  누르면 비활성화
class EnableStatus(ndb.Model):
    enabled = ndb.BooleanProperty(required=True, indexed=True, default=False,)

def get_restaurant_info(chat_id, result, location, menu, menu_detail):
    
#     html = urllib.urlopen("http://www.diningcode.com/list.php?query=" + location + "+" + menu)
    html = urllib2.urlopen("http://www.diningcode.com/list.php?query=사당역+한식")
    soup = BeautifulSoup(html.read(), "html.parser")

 
    list1 = soup.find_all("div", {"id" : "search_list"})
    index = 0
    
    send_msg(chat_id, len(list1).text)
    while index < 3 * 3:
        for restaurants in list1:
            send_msg(chat_id, u'식당찾기')
            tmp = []
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
            
        return result

def set_enabled(chat_id, enabled):
    u"""set_enabled: 봇 활성화/비활성화 상태 변경
    chat_id:    (integer) 봇을 활성화/비활성화할 채팅 ID
    enabled:    (boolean) 지정할 활성화/비활성화 상태
    """
    es = EnableStatus.get_or_insert(str(chat_id))
    es.enabled = enabled
    es.put()

def get_enabled(chat_id):
    u"""get_enabled: 봇 활성화/비활성화 상태 반환
    return: (boolean)
    """
    es = EnableStatus.get_by_id(str(chat_id))
    if es:
        return es.enabled
    return False

def get_enabled_chats():
    u"""get_enabled: 봇이 활성화된 채팅 리스트 반환
    return: (list of EnableStatus)
    """
    query = EnableStatus.query(EnableStatus.enabled == True)
    return query.fetch()

# 메시지 발송 관련 함수들
def send_msg(chat_id, text, reply_to=None, no_preview=True, keyboard=None):
    u"""send_msg: 메시지 발송
    chat_id:    (integer) 메시지를 보낼 채팅 ID
    text:       (string)  메시지 내용
    reply_to:   (integer) ~메시지에 대한 답장
    no_preview: (boolean) URL 자동 링크(미리보기) 끄기
    keyboard:   (list)    커스텀 키보드 지정
    """
    params = {
        'chat_id': str(chat_id),
        'text': text.encode('utf-8'),
        }
    if reply_to:
        params['reply_to_message_id'] = reply_to
    if no_preview:
        params['disable_web_page_preview'] = no_preview
    if keyboard:
        reply_markup = json.dumps({
            'keyboard': keyboard,
            'resize_keyboard': True,
            'one_time_keyboard': False,
            'selective': (reply_to != None),
            })
        params['reply_markup'] = reply_markup
    try:
        urllib2.urlopen(BASE_URL + 'sendMessage', urllib.urlencode(params)).read()
    except Exception as e: 
        logging.exception(e)

def broadcast(text):
    u"""broadcast: 봇이 켜져 있는 모든 채팅에 메시지 발송
    text:       (string)  메시지 내용
    """
    for chat in get_enabled_chats():
        send_msg(chat.key.string_id(), text)

# 봇 명령 처리 함수들
def cmd_start(chat_id):
    u"""cmd_start: 봇을 활성화하고, 활성화 메시지 발송
    chat_id: (integer) 채팅 ID
    """
    set_enabled(chat_id, True)
    send_msg(chat_id, MSG_START, keyboard=CUSTOM_KEYBOARD)

def cmd_stop(chat_id):
    u"""cmd_stop: 봇을 비활성화하고, 비활성화 메시지 발송
    chat_id: (integer) 채팅 ID
    """
    set_enabled(chat_id, False)
    send_msg(chat_id, MSG_STOP)

def cmd_help(chat_id):
    u"""cmd_help: 봇 사용법 메시지 발송
    chat_id: (integer) 채팅 ID
    """
    send_msg(chat_id, USAGE, keyboard=CUSTOM_KEYBOARD)

def cmd_broadcast(chat_id, text):
    u"""cmd_broadcast: 봇이 활성화된 모든 채팅에 메시지 방송
    chat_id: (integer) 채팅 ID
    text:    (string)  방송할 메시지
    """
    send_msg(chat_id, u'메시지를 방송합니다.', keyboard=CUSTOM_KEYBOARD)
    broadcast(text)

def cmd_echo(chat_id, text, reply_to):
    u"""cmd_echo: 사용자의 메시지를 따라서 답장
    chat_id:  (integer) 채팅 ID
    text:     (string)  사용자가 보낸 메시지 내용
    reply_to: (integer) 답장할 메시지 ID
    """
    send_msg(chat_id, text, reply_to=reply_to)

def search_restaurant(chat_id):
    global menu_detail
    global location
    global CLOUDSQL_PROJECT
    global CLOUDSQL_INSTANCE
    
    
    if os.getenv('SERVER_SOFTWARE', '').startswith('Google App Engine/'):
            db = MySQLdb.connect(
                unix_socket='/cloudsql/{}:{}'.format(
                    CLOUDSQL_PROJECT,
                    CLOUDSQL_INSTANCE),
                user='root')
    
    cursor = db.cursor()
    
    db.query("set character_set_connection=utf8;")
    db.query("set character_set_server=utf8;")
    db.query("set character_set_client=utf8;")
    db.query("set character_set_results=utf8;")
    db.query("set character_set_database=utf8;")
    
    cursor.execute("select minorName, resName, url, address, tel from category.restaurant where minorName = '"+ menu_detail + "'")
    results = cursor.fetchall()
    
    all_res = []
    all_url = []
    all_address = []
    all_tel = []
    recommend_number = 0
    
    for row in results:
        all_res.append(row[1])
        all_url.append(row[2])
        all_address.append(row[3])
        all_tel.append(row[4])
        
    recommend_number = random.randrange(0,len(all_res))

       
    
    msg_text = location + u' ' + menu_detail + u'전문점 ' + all_res[recommend_number] + u'\n주소 : ' +all_address[recommend_number] +  u'\n전화번호 : ' + all_tel[recommend_number] + u'\nURL :' + all_url[recommend_number]
    send_msg(chat_id, msg_text)

def random_menu(chat_id):
    global menu
    global CLOUDSQL_PROJECT
    global CLOUDSQL_INSTANCE
    global rejectMenu
    global nowNumber
    
    if os.getenv('SERVER_SOFTWARE', '').startswith('Google App Engine/'):
            db = MySQLdb.connect(
                unix_socket='/cloudsql/{}:{}'.format(
                    CLOUDSQL_PROJECT,
                    CLOUDSQL_INSTANCE),
                user='root')
    
    cursor = db.cursor()
    
    db.query("set character_set_connection=utf8;")
    db.query("set character_set_server=utf8;")
    db.query("set character_set_client=utf8;")
    db.query("set character_set_results=utf8;")
    db.query("set character_set_database=utf8;")
    
    cursor.execute('select * from category.major')
    results = cursor.fetchall()
    
    majorMenu = []
    for row in results:
        majorMenu.append(row[0])
    menuNumber = random.randrange(0,len(majorMenu))
    while True :
        menuNumber = random.randrange(0,len(majorMenu))
        if (menuNumber in rejectMenu):
            menuNumber = 0
        else :
            break
    nowNumber = menuNumber
    menu = majorMenu[menuNumber]
    msg_text = u'오늘 메뉴로 ' + menu + u'어떠세요?'
    send_msg(chat_id, msg_text)
    
    
    
def random_menu_detail(chat_id):
    global process
    global menu
    global menu_detail
    global nowNumber
    global rejectMenu
    global CLOUDSQL_PROJECT
    global CLOUDSQL_INSTANCE
    
    if os.getenv('SERVER_SOFTWARE', '').startswith('Google App Engine/'):
            db = MySQLdb.connect(
                unix_socket='/cloudsql/{}:{}'.format(
                    CLOUDSQL_PROJECT,
                    CLOUDSQL_INSTANCE),
                user='root')
    
    cursor = db.cursor()
    
    db.query("set character_set_connection=utf8;")
    db.query("set character_set_server=utf8;")
    db.query("set character_set_client=utf8;")
    db.query("set character_set_results=utf8;")
    db.query("set character_set_database=utf8;")
    
    
    cursor.execute("select minorName from category.minor where majorName = '" + menu + "'")
    results = cursor.fetchall()
    
    minorMenu = []
    for row in results:
        minorMenu.append(row[0])
#     menu = u'한식'
    while True :
        menuNumber = random.randrange(0,len(minorMenu))
        if (menuNumber in rejectMenu):
            menuNumber = 0
        else :
            break
    nowNumber = menuNumber
    menu_detail = minorMenu[menuNumber]
    
    if process == 6:
        msg_text = u'세부 메뉴를 추천해 드릴게요. \n' + menu_detail + u'은(는) 어떠세요?'
        send_msg(chat_id, msg_text)
        return
    
def process_cmds(msg):
    u"""사용자 메시지를 분석해 봇 명령을 처리
    chat_id: (integer) 채팅 ID
    text:    (string)  사용자가 보낸 메시지 내용
    """
    msg_id = msg['message_id']
    chat_id = msg['chat']['id']
    text = msg.get('text')

    global process, menu, menu_detail, location
    global rejectMenu
    global nowNumber
    if (not text):
        return
    if CMD_START == text:
        process = 2
        cmd_start(chat_id)
        return
    if (not get_enabled(chat_id)):
        return
    if CMD_STOP == text:
        process = 0
        cmd_stop(chat_id)
        return
    if CMD_HELP == text:
        cmd_help(chat_id)
        return
    
    if process == 1:  # 다시 검색할 때 (TODO:함수로 만들어야함)
        msg_text = u'현재 계신 곳의 위치 또는 식사할 위치를 알려주세요.'
        send_msg(chat_id, msg_text)
        process = process + 1
        return
    
    if process == 2:
        # LOCATION 변수에 유저가 입력한 지역저장
        location = text.encode('utf-8')         
        # DB에서 지역 검색 
        msg_text = location
        msg_text += u'이(가) 맞으신가요? 아니라면 "아니"를 입력해 주시고, \n맞으면 원하시는 메뉴를 말씀해 주세요.\n\n'
        msg_text += u'원하시는 메뉴가 없다면 "아무거나"를 입력해 주세요.'
        send_msg(chat_id, msg_text)
        process = process + 1
        return
    
    if process == 3:
        if u'아니' == text:
            process = 1
            process_cmds(' ')
        elif u'아무거나' == text:
            random_menu(chat_id);
            process = process + 1
        else:
            # MENU 변수에 유저가 입력한 메뉴저장
            menu = text.encode('utf-8')
            msg_text = location
            msg_text += " "
            msg_text += menu
            msg_text += u' (을)를 빠르게 찾아드릴게요~\n잠시만 기다려주세요.'
            send_msg(chat_id, msg_text)
            process = 7
            random_menu_detail(chat_id)
            process_cmds(msg)
        return
    
    if process == 4:  # '아무거나' 메뉴추천
        if u'싫어' == text:
            msg_text = u'네, 다른 메뉴를 추천해 드릴게요.'
            
            rejectMenu.append(nowNumber)
            
            send_msg(chat_id, msg_text)
            random_menu(chat_id)
            return
        elif u'좋아' == text:
            msg_text = menu + u' 이(가) 좋으시군요.'
            
            nowNumber = -1
            del rejectMenu[0:len(rejectMenu)]
            
             
            send_msg(chat_id, msg_text)
            process = process + 2
            random_menu_detail(chat_id)
        return
    

        if u'싫어' == text:
            msg_text = u'네, 다른 메뉴를 추천해 드릴게요.'
            
            rejectMenu.append(nowNumber)
            
            send_msg(chat_id, msg_text)
            random_menu_detail(chat_id)
            return
        elif u'좋아' == text:
            msg_text = menu_detail + u' 이(가) 좋으시군요.\n' + location + " " + menu + " " + menu_detail 
            msg_text += u'을(를) 빠르게 찾아드릴게요~\n잠시만 기다려주세요.' 
            
            nowNumber = -1
            del rejectMenu[0:len(rejectMenu)]
            
            send_msg(chat_id, msg_text)
            process = process + 1
            process_cmds(msg)
        return
    
    if process == 7:
        search_restaurant(chat_id)

        return

    
    
            
# 웹 요청에 대한 핸들러 정의
# /me 요청시
class MeHandler(webapp2.RequestHandler):
    def get(self):
        urlfetch.set_default_fetch_deadline(60)
        self.response.write(json.dumps(json.load(urllib2.urlopen(BASE_URL + 'getMe'))))

# /updates 요청시
class GetUpdatesHandler(webapp2.RequestHandler):
    def get(self):
        urlfetch.set_default_fetch_deadline(60)
        self.response.write(json.dumps(json.load(urllib2.urlopen(BASE_URL + 'getUpdates'))))

# /set-wehook 요청시
class SetWebhookHandler(webapp2.RequestHandler):
    def get(self):
        urlfetch.set_default_fetch_deadline(60)
        url = self.request.get('url')
        if url:
            self.response.write(json.dumps(json.load(urllib2.urlopen(BASE_URL + 'setWebhook', urllib.urlencode({'url': url})))))

# /webhook 요청시 (텔레그램 봇 API)
class WebhookHandler(webapp2.RequestHandler):
    def post(self):
        urlfetch.set_default_fetch_deadline(60)
        body = json.loads(self.request.body)
        self.response.write(json.dumps(body))
        process_cmds(body['message'])
        
class CrawlingHandler(webapp2.RequestHandler):
    def get(self):
        global cid
        html = urllib2.urlopen('http://www.diningcode.com/list.php?query=사당역+한식')
        soup = BeautifulSoup(html.read(), "html.parser")
        
        list = soup.find_all("div", {"id" : "search_list"})
        index = 0
        self.response.write('asdfasdfasdf')
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
                send_msg(cid, result[0].decode('utf-8').encode('utf-8'))
            #self.response.write(result)

# 구글 앱 엔진에 웹 요청 핸들러 지정
app = webapp2.WSGIApplication([
    ('/me', MeHandler),
    ('/updates', GetUpdatesHandler),
    ('/set-webhook', SetWebhookHandler),
    ('/webhook', WebhookHandler)
], debug=True)
