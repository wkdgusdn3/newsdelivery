# -*- coding: utf-8 -*-

from flask import *
from os import urandom
import pymysql
import datetime
import socket

app = Flask(__name__)
app.secret_key = urandom(16)

# aws db 연결
def setDB() :
    host = "wkdgusdn3.cqvehrgls7j9.ap-northeast-2.rds.amazonaws.com"
    id = "wkdgusdn3"
    password = "wkdgusdn3"
    name = "news_delivery"
    # name = "news_delivery_test"

    db = pymysql.connect(host, id, password, name, charset="utf8")

    return db

# pi db 연결
def setDB_pi() :
    host = "localhost"
    id = "root"
    password = "wkdgusdn3"
    name = "news_delivery"

    db = pymysql.connect(host, id, password, name, charset="utf8")

    return db

@app.before_request
def before_request():
	hostname = socket.gethostname()

	if hostname == "raspberrypi" :
	    g.db = setDB_pi()
	else :
	    g.db = setDB()

@app.teardown_request
def teardown_request(exception):
	g.db.close()

# default route
@app.route('/')
def index():
	return redirect(url_for('main'))

# main page
@app.route('/main')
def main():
	if('email' in session): # 세션 성공
		return render_template('main.html', is_authenticated=True,
				email=session['email'], seq=session['seq'])
	else: # 세션 실패
		return render_template("main.html")

# 키워드 관리 page
@app.route('/delivered_news')
def deliveredNews():
	if('email' in session): # 세션 성공

		seq = session['seq']

		today = datetime.date.today()
		tomorrow = today + datetime.timedelta(days = 1)

		cur = g.db.cursor()
		cur.execute("SELECT delivery_log.seq, company, keyword, crawling_news.seq, title, crawling_news.date FROM delivery_log, crawling_news WHERE delivery_log.news_seq = crawling_news.seq AND delivery_log.user_seq = '%s' AND crawling_news.date BETWEEN '%s' AND '%s' ORDER BY date;" %(seq, today, tomorrow)) # 등록된 키워드 정보를 가져오기
		rows = cur.fetchall()

		passNews = []

		for row in rows :
			# passNews.append("http://localhost:5000/passnews?news_seq=%s&delivery_seq=%s" %(row[3], row[0]))
			passNews.append("http://newsdelivery.co.kr/passnews?news_seq=%s&delivery_seq=%s" %(row[3], row[0]))

		return render_template('delivered_news.html', is_authenticated=True,
				email=session['email'], seq=session['seq'], rows=rows, passNews=passNews, zip=zip)
	else: # 세션 실패
		return render_template("signin.html")

# 키워드 관리 page
@app.route('/manage_keyword')
def manageKeyword():
	if('email' in session): # 세션 성공

		seq = session['seq']

		cur = g.db.cursor()
		cur.execute("SELECT * FROM keyword WHERE user_seq='%s' ORDER BY company, keyword" %(seq)) # 등록된 키워드 정보를 가져오기
		rows = cur.fetchall()

		return render_template('manage_keyword.html', is_authenticated=True,
				email=session['email'], seq=session['seq'], rows=rows)
	else: # 세션 실패
		return render_template("signin.html")

# 회원 정보 관리 page
@app.route('/manage_info')
def manageInfo():
	if('email' in session): # 세션 성공

		seq = session['seq']

		cur = g.db.cursor()
		cur.execute("SELECT birth, sex, realtime_delivery, daily_delivery FROM user WHERE seq = '%s'" %(seq))
		rows = cur.fetchall()

		return render_template('manage_info.html', is_authenticated=True,
				email=session['email'], seq=session['seq'], birth = rows[0][0], sex = rows[0][1], realTimeDelivery = rows[0][2], dailyDelivery = rows[0][3])
	else: # 세션 실패
		return render_template("signin.html")

# 회원 가입 page
@app.route('/signup')
def signUp():
	return render_template("signup.html")

# 로그인 page
@app.route('/signin')
def signIn():
	return render_template("signin.html")

# 로그인 요청
@app.route('/signin/signin', methods=['POST'])
def signIn_signIn() :
	email = request.form.get("email")
	password = request.form.get("password")

	cur = g.db.cursor();
	cur.execute("SELECT seq, email FROM user WHERE email='%s' AND password='%s'" %(email, password))	# email, 비밀번호 확인
	rows = cur.fetchall()

	if len(rows) == 0 :	# 로그인 실패
		return jsonify({"status": "fail"})	# 로그인 실패
	else : # 로그인 성공
		session['email'] = rows[0][1]
		session['seq'] = rows[0][0]

		cur.execute("INSERT INTO login_log(user_seq) VALUES('%s')" %(rows[0][0]))
		g.db.commit()

		if('email' in session) : # 세션 성공
			return jsonify({"status": "success"})
		else: # 세션 실패
			return jsonify({"status": "fail"})	# 로그인 실패

# 회원가입 요청
@app.route('/signup/signup', methods=['POST'])
def signUp_signUp():

	email = request.form.get("email")
	password = request.form.get("password")
	birth = request.form.get("birth")
	sex = request.form.get("sex")

	cur = g.db.cursor()
	cur.execute("SELECT * FROM user WHERE email='%s'" %(email))	# email이 중복되는지 확인하기 위해 query 사용
	rows = cur.fetchall()

	if len(rows) == 0 :		# 회원가입 성공
		cur.execute("INSERT INTO user(email, password, birth, sex) VALUES('%s', '%s', '%s', '%s')" %(email, password, birth, sex)) 
		g.db.commit()
		return jsonify({"status": "success"})	
	else :			# 회원가입 실패
		return jsonify({"status": "fail"})

# 로그아웃
@app.route("/logout", methods=["POST"])
def logOut() :
	session.clear() # 세션 지움
	return jsonify({"status": "success"})

# 키워드 등록
@app.route("/register_keyword/insert", methods=["POST"])
def registerKeyword_insert() :
	seq = request.form.get("seq")
	keyword = request.form.get("keyword")
	company = request.form.get("company")

	# keyword table에 keyword 추가
	cur = g.db.cursor()
	cur.execute("INSERT INTO keyword(user_seq, keyword, company) VALUES('%s', '%s', '%s')" %(seq, keyword, company)) 
	g.db.commit()

	return jsonify({"status": "success"})

# 회원정보 업데이트
@app.route('/manage_info/update', methods=['POST'])
def manageInfo_update():

	seq = request.form.get("seq")
	password = request.form.get("password")
	birth = request.form.get("birth")
	sex = request.form.get("sex")
	realTimeDelivery = request.form.get("realTimeDelivery") == "true" and 1 or 0
	dailyDelivery = request.form.get("dailyDelivery") == "true" and 1 or 0

	cur = g.db.cursor()

	# 회원정보 업데이트
	if password == None :
		cur.execute("UPDATE user SET birth = '%s', sex = '%s', realtime_delivery = '%s', daily_delivery = '%s' WHERE seq = '%s'" %(birth, sex, realTimeDelivery, dailyDelivery, seq))
	else :
		cur.execute("UPDATE user SET password = '%s', birth = '%s', sex = '%s', realtime_delivery = '%s', daily_delivery = '%s' WHERE seq = '%s'" %(password, birth, sex, realTimeDelivery, dailyDelivery, seq))
	
	g.db.commit()	

	return jsonify({"status": "success"})	

# 키워드 삭제
@app.route('/manage_keyword/delete', methods=['POST'])
def manageKeyword_delete():

	seq = request.form.get("seq")
	keyword = request.form.getlist("keyword[]")
	company = request.form.getlist("company[]")

	cur = g.db.cursor()

	i = 0

	# 키워드 삭제
	for i in range(0, len(keyword)) :
		cur.execute("DELETE FROM keyword WHERE user_seq = '%s' AND keyword = '%s' AND company = '%s'" %(seq, keyword[i], company[i]))

	g.db.commit()

	return jsonify({"status": "success"})	

# pass news
@app.route('/passnews', methods=['GET'])
def passNews():

	newsSeq = request.args.get("news_seq", '')
	deliverySeq = request.args.get("delivery_seq", '')
	

	cur = g.db.cursor()

	updateQuery = "UPDATE delivery_log SET view_count = view_count + 1 WHERE seq = '%s'" %(deliverySeq)
	cur.execute(updateQuery)
	g.db.commit()

	selectQuery = "SELECT url FROM crawling_news WHERE seq = '%s'" %(newsSeq)
	cur.execute(selectQuery)
	rows = cur.fetchall()

	return redirect(rows[0][0])


if __name__ == "__main__": 
	app.run(debug=True)
	# app.run(host="0.0.0.0", port=5000)