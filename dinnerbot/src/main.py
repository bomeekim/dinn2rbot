# -*- coding: utf-8 -*-
#
# original:    https://github.com/yukuku/telebot
# modified by: Bak Yeon O @ http://bakyeono.net
# description: http://bakyeono.net/post/2015-08-24-using-telegram-bot-api.html
# github:      https://github.com/bakyeono/using-telegram-bot-api
#

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

#크롤링
# from bs4 import BeautifulSoup 
# 봇 토큰, 봇 API 주소
TOKEN = '222474870:AAFJkDwrJ0BnqQI3IKwRr4S0PDf89brjJQE'
BASE_URL = 'https://api.telegram.org/bot' + TOKEN + '/'

# 봇이 응답할 명령어
CMD_START = '/start'
CMD_STOP = '/stop'
CMD_HELP = '/help'
CMD_BROADCAST = '/broadcast'

# 전역변수
process = 0
menu = u'한식'
location = u'사당'

# 봇 사용법 & 메시지
USAGE = u"""[사용법] 아래 명령어를 메시지로 보내거나 버튼을 누르시면 됩니다.
/start - (봇 활성화)
/stop  - (봇 비활성화)
/help  - (이 도움말 보여주기)
"""
MSG_START = u'봇을 시작합니다.'
MSG_STOP = u'봇을 정지합니다.'

# 커스텀 키보드
CUSTOM_KEYBOARD = [
        [CMD_START],
        [CMD_STOP],
        [CMD_HELP],
        ]

# 채팅별 봇 활성화 상태
# 구글 앱 엔진의 Datastore(NDB)에 상태를 저장하고 읽음
# 사용자가 /start 누르면 활성화
# 사용자가 /stop  누르면 비활성화
class EnableStatus(ndb.Model):
    enabled = ndb.BooleanProperty(required=True, indexed=True, default=False,)

# def getData(location, menu):
#     html = urllib.urlopen("http://www.diningcode.com/list.php?query=" + location + "+" + menu)
#     soup = BeautifulSoup(html.read(), "html.parser")
# 
#     list = soup.find_all("div", {"id" : "search_list"})
#     index = 0
# 
#     while index < 30 * 3:
#         for restaurants in list:
#             name_and_link = restaurants.find_all("a")[index]
#             name = name_and_link.text.encode('utf-8')
#             link = "http://www.diningcode.com/" + name_and_link["href"].split("&")[0]
#     
#             info = restaurants.find_all("div", {"class" : "dc-restaurant-info"})
#             keyword = info[index].text.encode('utf-8').replace('\n', '')
#             address = info[index + 1].text.encode('utf-8').replace('\n', '')
#             tel = info[index + 2].text.encode('utf-8').replace('\n', '')
#             index = index + 3
#     
#             print name, link, keyword, address, tel
#             result = name + link + keyword + address + tel
#     
#     return result

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

def process_cmds(msg):
    u"""사용자 메시지를 분석해 봇 명령을 처리
    chat_id: (integer) 채팅 ID
    text:    (string)  사용자가 보낸 메시지 내용
    """
    msg_id = msg['message_id']
    chat_id = msg['chat']['id']
    text = msg.get('text')
    global process
    if (not text):
        return
    if CMD_START == text:
        process = 0
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
    if(process == 0):  # 여친컨셉은 어때?
        if u'최비서' == text:
            msg_text = u'네. 메뉴 정하기를 책임질 소프트웨어학과 최성신입니다. 메뉴 찾기를 실행하시겠습니까?'
            send_msg(chat_id, msg_text)
            process = process + 1
            return
        return
    if(process == 1):
        if u'응' == text:
            msg_text = u'네, 알겠습니다. 현재계신 위치 또는 식사를 할 위치를 알려주세요'
            send_msg(chat_id, msg_text)
            location = msg_text
            process = process + 1
            return
        return
    if(process == 2):
        # DB에서 지역 검색 
        msg_text = u'사당이 맞습니까? 아니라면 "아니"를 입력해 주시고, 맞으면 원하시는 메뉴를 말씀해 주세요.'
        msg_text += u'원하시는 메뉴가 없다면 "random" 또는 "아무거나"를 입력해 주세요.'
         
        send_msg(chat_id, msg_text)          
        process = process + 1
        return
    if(process == 3):
        if u'아니' == text:
            process = 1
        elif u'아무거나' or u'random':
            process = process + 1    
        else :
            process = process + 2
            return
         
        return
    if(process == 4):  # random 추천
        # 맛집 분류를 DB에 저장 후 랜덤으로 추출. url쿼리는 '지역 + 랜덤 맛집 분류' 
        menu = u'한식'
        # 실험용. 메뉴 랜덤으로 추출하는 함수 만들기. 
        msg_text = u'그렇다면, 오늘 메뉴로' + menu + u'어떠세요? 싫으시면 "싫어"를 입력해 주세요.'
        send_msg(chat_id, msg_text)
        process = process + 1
        return
    if(process == 5):
        if(u'싫어' == text):
            process = 4
        else :
            # 서치하는 함수
#             result = getData(location, menu)
#             send_msg(chat_id,result)
            return
        return
        
    cmd_broadcast_match = re.match('^' + CMD_BROADCAST + ' (.*)', text)
    if cmd_broadcast_match:
        cmd_broadcast(chat_id, cmd_broadcast_match.group(1))
        return
    cmd_echo(chat_id, text, reply_to=msg_id)
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

# 구글 앱 엔진에 웹 요청 핸들러 지정
app = webapp2.WSGIApplication([
    ('/me', MeHandler),
    ('/updates', GetUpdatesHandler),
    ('/set-webhook', SetWebhookHandler),
    ('/webhook', WebhookHandler),
], debug=True)
