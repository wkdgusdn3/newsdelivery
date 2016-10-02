import requests
from bs4 import BeautifulSoup
import pymysql
import re
import sys
import smtplib
import email
import time

from email.mime.text import MIMEText
from email.header import Header

# database 연결
def setDB() :
    host = "wkdgusdn3.cqvehrgls7j9.ap-northeast-2.rds.amazonaws.com"
    id = "wkdgusdn3"
    password = "wkdgusdn3"
    name = "news_delivery"

    db = pymysql.connect(host, id, password, name, charset="utf8")

    return db

# database에서 keyword를 가져온다
def getKeyword() :
    query = "SELECT user.seq, email, keyword, company FROM keyword, user WHERE keyword.user_seq = user.seq"
    cur.execute(query)

    keyword = cur.fetchall()

    return keyword

# email 연결
def connectEmail() :
    global myemail
    global sender
    global smtp

    myemail = ('뉴스배달', 'newsdelivery33@gmail.com')
    myemail = email.utils.formataddr(myemail)

    sender = "newsdelivery33@gmail.com"

    smtp = smtplib.SMTP("smtp.gmail.com", 587)
    smtp.ehlo()
    smtp.starttls()
    passwd = "wkd12345!@"
    smtp.login(sender, passwd)
    
# 이메일 전송
def sendEmail(email, content):
    now = time.localtime()
    
    subject = str(now.tm_year) + "." + str(now.tm_mon) + "." + str(now.tm_mday) + " Daily 뉴스 배달입니다."
    message = content

    mail_to = []
    mail_to.append(email)

    msg = MIMEText(message.encode('utf-8'), _subtype='plain', _charset='utf-8')
    msg['Subject'] = Header(subject.encode('utf-8'), 'utf-8')
    msg['From'] = myemail
    msg['To'] = ','.join(mail_to)

    smtp.sendmail(myemail, mail_to, msg.as_string( ))

def sendDailyDelivery():
    now = time.localtime()
    today = str(now.tm_year) + "." + str(now.tm_mon) + "." + str(now.tm_mday) # 오늘의 날짜
    tomorrow = str(now.tm_year) + "." + str(now.tm_mon) + "." + str(now.tm_mday+1) # 내일의 날짜
    
    query = "SELECT email, title, company, url FROM delivery_log, user, crawling_news WHERE user.seq = delivery_log.user_seq AND crawling_news.seq = delivery_log.news_seq AND crawling_news.date BETWEEN '%s' AND '%s' AND user.daily_delivery = 1 ORDER BY email" %(today, tomorrow)
    cur.execute(query)
    
    rows = cur.fetchall()

    email = ""
    content = ""
    
    if len(rows) > 0 :
        email = rows[0][0] # 이메일 설정
        content = ""
        
        for i in rows :
            if email == i[0] : # 이메일이 같을경우
                # 기사, 신문사, url 추가
                content += i[1] + "\n"
                content += i[2] + "\n"
                content += i[3] + "\n\n"
            else :
                sendEmail(email, content) # daily email 전송

                email = i[0] # 이메일 초기화
                content = "" # 내용 초기화
                content += i[1] + "\n"
                content += i[2] + "\n"
                content += i[3] + "\n\n"
               
        sendEmail(email, content) # 마지막 user에게 이메일 전송
    
global db
global cur

db = setDB()
cur = db.cursor()

connectEmail() # 이메일 연결
sendDailyDelivery() # 데일리 리포트 전송
