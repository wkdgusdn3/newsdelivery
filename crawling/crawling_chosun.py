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
    password = "wkdgusdn3"
    name = "news_delivery"

    db = pymysql.connect(host, id, password, name, charset="utf8")

    return db

# 뉴스 리스트 크롤링
def newsListCrawling(url) :

    count = 0;
    while True :
        count += 1
        subUrl = url + str(count)   # url 생성
        r = requests.get(subUrl)
        r.encoding = "euc-kr"
        html = r.text
        soup = BeautifulSoup(html, "lxml")  # html을 beautifulsoup으로 생성

        for i in soup.select("div .list_item"): # 각각의 기사

            temp = i.select("dt a")[0]
            title = pymysql.escape_string(temp.text)    # get title
            newsUrl = temp["href"]  # get news url
            date = i.select(".date_author span")[0].text.split(" ")[0] # get date

            # 이전에 등록된 기사인지 확인
            query = "SELECT * FROM crawling_news WHERE url = '%s'" %(newsUrl)
            cur.execute(query)

            if cur.rowcount == 0 :  # 이전에 등록한 뉴스가 아니면

                query = "INSERT INTO crawling_news(title, company, url, date) VALUE('%s', '%s', '%s', '%s');" %(title, '조선일보', newsUrl, date)   # 뉴스 insert
                cur.execute(query)
                news_seq = cur.lastrowid;   # 가장 큰 seq get

                print(title)

                newsDetailCrawling(newsUrl) # news의 세부기사 크롤링

                for i in keyword :
                    if i[2] in title and i[3] == '조선일보' :   # 등록된 키워드이면
                        sendEmail(i[0], i[1], i[2], title, newsUrl, news_seq) # 메일로 전송
            else :  # 이전에 등록한 뉴스이면 종료
                db.commit()
                smtp.quit()
                sys.exit()

        if count == 100 :   # 최대 100page까지만 크롤링
            sys.exit()
            smtp.quit()

        db.commit()

# 뉴스 기사 크롤링
def newsDetailCrawling(url) :
    r = requests.get(url)
    r.encoding = "euc-kr"
    html = r.text
    soup = BeautifulSoup(html, 'lxml')

    time = soup.select(".date_ctrl_2011 p")[0].text.strip()[5:20] # time get

    # 기사 내용 get
    content = "";
    for i in soup.select(".par") :
        content += i.text

    content = pymysql.escape_string(content)

    # update문을 통해서 기사 udpate
    query = "UPDATE crawling_news SET date = '%s', content = '%s' WHERE url = '%s'" %(time, content, url)
    cur.execute(query)

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
    passwd = "wkdgusdn3"
    smtp.login(sender, passwd)

# 이메일 전송
def sendEmail(user_seq, email, keyword, title, url, news_seq):
    subject = keyword + "에 대한 뉴스배달입니다."
    message = title + "\n" + "조선일보\n\n" + url 

    mail_to = []
    mail_to.append(email)

    msg = MIMEText(message.encode('utf-8'), _subtype='plain', _charset='utf-8')
    msg['Subject'] = Header(subject.encode('utf-8'), 'utf-8')
    msg['From'] = myemail
    msg['To'] = ','.join(mail_to)

    # 이메일 전송
    smtp.sendmail(myemail, mail_to, msg.as_string( ))
    # 뉴스 배달 로그 저장
    query = "INSERT INTO delivery_log(user_seq, news_seq) VALUE('%s', '%s');" %(user_seq, news_seq)
    cur.execute(query)

    # print("send : " + "wkdgusdn3@naver.com " + title)

global db
global cur

db = setDB()
cur = db.cursor()

url = "http://news.chosun.com/svc/list_in/list.html?pn=" # 조선일보 전체뉴스보는 url

keyword = getKeyword()  # 등록된 키워드 get
connectEmail()  # 이메일 연결
newsListCrawling(url) # 뉴스 크롤링