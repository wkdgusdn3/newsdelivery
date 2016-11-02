import requests
from bs4 import BeautifulSoup
import pymysql
import re
import sys
import smtplib
import email
import datetime

from email.mime.text import MIMEText
from email.header import Header

# database 연결
def setDB() :
    host = "wkdgusdn3.cqvehrgls7j9.ap-northeast-2.rds.amazonaws.com"
    id = "wkdgusdn3"
    # host = "localhost"
    # id = "root"
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
    now = datetime.date.today()
    
    subject = str(now.year) + "." + str(now.month) + "." + str(now.day) + " Daily 뉴스 배달입니다."
    message = content

    mail_to = []
    mail_to.append(email)

    msg = MIMEText(message, 'html')
    msg['Subject'] = Header(subject.encode('utf-8'), 'utf-8')
    msg['From'] = myemail
    msg['To'] = ','.join(mail_to)

    smtp.sendmail(myemail, mail_to, msg.as_string( ))

def sendDailyDelivery():
    today = datetime.date.today()   # 오늘 날짜
    tomorrow = today + datetime.timedelta(days = 1) # 내일 날짜
    
    query = "SELECT email, title, company, url, crawling_news.date FROM delivery_log, user, crawling_news WHERE user.seq = delivery_log.user_seq AND crawling_news.seq = delivery_log.news_seq AND crawling_news.date BETWEEN '%s' AND '%s' AND user.daily_delivery = 1 ORDER BY email, date" %(today, tomorrow)
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
                content += "<a href='%s'>%s</a><br>" %(i[3], i[1])
                content += str(i[4]) + "<br>"
                content += i[2] + "<br><br>"

            else :
                sendEmail(email, content) # daily email 전송

                email = i[0] # 이메일 초기화
                content = "" # 내용 초기화
                content += "<a href='%s'>%s</a><br>" %(i[3], i[1])
                content += str(i[4]) + "<br>"
                content += i[2] + "<br><br>"

        sendEmail(email, content) # 마지막 user에게 이메일 전송
    
global db
global cur

db = setDB()
cur = db.cursor()

connectEmail() # 이메일 연결
sendDailyDelivery() # 데일리 리포트 전송
