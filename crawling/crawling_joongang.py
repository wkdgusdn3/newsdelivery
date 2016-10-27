# coding: utf-8

import requests
from bs4 import BeautifulSoup
import pymysql
import re
import sys
import smtplib
import email
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


db = setDB()
cur = db.cursor()

def newsCrawling() :
    url1 = "http://news.joins.com/article/"
    
    query = "SELECT url FROM crawling_news WHERE company = '중앙일보' ORDER BY seq DESC LIMIT 1"
    cur.execute(query)

    latelyUrl = cur.fetchall()[0][0]
    latelySeq = int(latelyUrl.split("?")[0].split("/")[-1]) + 1
    print(latelySeq)
    
    exceptCount = 0
    
    while True :
        try :
            newsUrl = url1 + str(latelySeq)
            r = requests.get(newsUrl)
            r.encoding = "utf8"
            html = r.text
            soup = BeautifulSoup(html, "lxml")

            title = soup.select(".subject h1")[0].text.strip()
            category = soup.select("meta")[23]["content"]
            company = soup.select("div .byline em")[0].text
            date = soup.select("div .byline em")[1].text[3:]
            content = ""

            if company != "[중앙일보]" :
                continue

            for i in soup.select("#article_body") :
                content += i.text.strip()

            insertQuery = "INSERT INTO crawling_news(company, category, title, content, url, date) VALUES('중앙일보', '%s', '%s', '%s', '%s', '%s')" %(category, pymysql.escape_string(title), pymysql.escape_string(content), newsUrl, date)
            cur.execute(insertQuery)
            seq = db.insert_id()
            
            print(newsUrl)

            for i in keyword :
                if i[2] in title and (i[3] == '중앙일보' or i[3] == '전체'):   # 등록된 키워드이면
                    # 뉴스 배달 로그 저장
                    deliveryLogQuery = "INSERT INTO delivery_log(user_seq, news_seq, keyword) VALUE('%s', '%s', '%s');" %(i[0], seq, i[2])
                    cur.execute(deliveryLogQuery)
                    
                    if i[4] == 1 :
                        sendEmail(i[1], i[2], title, newsUrl) # 메일로 전송
            
            db.commit()

        except :
            print(newsUrl)
            print(sys.exc_info()[0])
            exceptCount += 1

            if exceptCount == 100 :
                break
                
        latelySeq += 1
        
    db.commit()
    smtp.quit()

# database에서 keyword를 가져온다
def getKeyword() :
    query = "SELECT user.seq, email, keyword, company, realtime_delivery FROM keyword, user WHERE keyword.user_seq = user.seq AND user.seq = 1"
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
def sendEmail(email, keyword, title, url):
    subject = keyword + "에 대한 뉴스배달입니다."
    message = "<a href='%s'>%s</a>" %(url, title)
    message += "<br>중앙일보"

    mail_to = []
    mail_to.append(email)

    msg = MIMEText(message, 'html')
    msg['Subject'] = Header(subject.encode('utf-8'), 'utf-8')
    msg['From'] = myemail
    msg['To'] = ','.join(mail_to)

    # 이메일 전송
    smtp.sendmail(myemail, mail_to, msg.as_string( ))

keyword = getKeyword()
connectEmail()
newsCrawling()