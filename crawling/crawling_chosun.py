import requests
from bs4 import BeautifulSoup
import pymysql
import re
import sys
import smtplib
import email
import socket
from email.mime.text import MIMEText
from email.header import Header

# database 연결
def setDB() :
    host = "wkdgusdn3.cqvehrgls7j9.ap-northeast-2.rds.amazonaws.com"
    id = "wkdgusdn3"
    password = "wkdgusdn3"
    name = "news_delivery"
    # name = "news_delivery_test"

    db = pymysql.connect(host, id, password, name, charset="utf8")

    return db

def setDB_pi() :
    host = "localhost"
    id = "root"
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
            try :
                temp = i.select("dt a")[0]
                title = temp.text    # get title
                newsUrl = temp["href"]  # get news url
                date = i.select(".date_author span")[0].text.split(" ")[0] # get date

                # 이전에 등록된 기사인지 확인
                query = "SELECT * FROM crawling_news WHERE url = '%s'" %(newsUrl)
                cur.execute(query)

                if cur.rowcount == 0 :  # 이전에 등록한 뉴스가 아니면

                    query = "INSERT INTO crawling_news(title, company, url, date) VALUE('%s', '%s', '%s', '%s');" %(pymysql.escape_string(title), '조선일보', newsUrl, date)   # 뉴스 insert
                    cur.execute(query)
                    newsSeq = cur.lastrowid   # 가장 큰 seq get

                    print(newsUrl)

                    newsDetailCrawling(newsUrl) # news의 세부기사 크롤링

                    # for i in keyword :
                    #     if i[2] in title and (i[3] == '조선일보' or i[3] == '전체'):   # 등록된 키워드이면
                    #         # 뉴스 배달 로그 저장
                    #         deliveryLogQuery = "INSERT INTO delivery_log(user_seq, news_seq, keyword) VALUE('%s', '%s', '%s');" %(i[0], newsSeq, i[2])
                    #         cur.execute(deliveryLogQuery)
                    #         deliverySeq = cur.lastrowid

                    #         if i[4] == 1 :
                                # sendEmail(i[1], i[2], title, newsSeq, deliverySeq) # 메일로 전송

                    db.commit()
                else :  # 이전에 등록한 뉴스이면 종료
                    db.commit()
                    smtp.quit()
                    sys.exit()
            except SystemExit :
                sys.exit()
            except :
                print("error : " + str(sys.exc_info()[0]))

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

    category = soup.select("title")[0].text.split("-")[-1].strip()
    time = soup.select(".date_ctrl_2011 p")[0].text.strip()[5:21] # time get

    # 기사 내용 get
    content = "";
    for i in soup.select(".par") :
        content += i.text

    content = pymysql.escape_string(content)

    # update문을 통해서 기사 udpate
    query = "UPDATE crawling_news SET category = '%s', date = '%s', content = '%s' WHERE url = '%s'" %(category, time, content, url)
    cur.execute(query)

# database에서 keyword를 가져온다
def getKeyword() :
    query = "SELECT user.seq, email, keyword, company, realtime_delivery FROM keyword, user WHERE keyword.user_seq = user.seq"
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
def sendEmail(email, keyword, title, newsSeq, deliverySeq):
    passUrl = "http://newsdelivery.co.kr/passnews?news_seq=%s&delivery_seq=%s" %(newsSeq, deliverySeq)
    # passUrl = "http://localhost:5000/passnews?news_seq=%s&delivery_seq=%s" %(newsSeq, deliverySeq)

    subject = keyword + "에 대한 뉴스배달입니다."
    message = """<a href="http://newsdelivery.co.kr"><img src="http://newsdelivery.co.kr/static/images/logo.png" style="width:150px"></a>
    <hr style="border-color:#2E75B6;"><br>"""
    message += "<a href='%s'>%s</a>" %(passUrl, title)
    message += "<br>조선일보"

    mail_to = []
    mail_to.append(email)

    msg = MIMEText(message, 'html')
    msg['Subject'] = Header(subject.encode('utf-8'), 'utf-8')
    msg['From'] = myemail
    msg['To'] = ','.join(mail_to)

    # 이메일 전송
    smtp.sendmail(myemail, mail_to, msg.as_string( ))

global db
global cur

hostname = socket.gethostname()

if hostname == "raspberrypi" :
    db = setDB_pi()
else :
    db = setDB()

cur = db.cursor()

url = "http://news.chosun.com/svc/list_in/list.html?pn=" # 조선일보 전체뉴스보는 url

keyword = getKeyword()  # 등록된 키워드 get
connectEmail()  # 이메일 연결
newsListCrawling(url) # 뉴스 크롤링
