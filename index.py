# -*- coding: utf-8 -*-

from flask import *
from os import urandom
import pymysql

app = Flask(__name__)
app.secret_key = urandom(16)

host = "wkdgusdn3.cqvehrgls7j9.ap-northeast-2.rds.amazonaws.com"
id = "wkdgusdn3"
password="wkdgusdn3"
name="news_delivery"

@app.before_request
def before_request():
	g.db = pymysql.connect(host, id, password, name, charset="utf8")

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
	if('email' in session): # ���� ����
		return render_template('main.html', is_authenticated=True,
				email=session['email'], seq=session['seq'])
	else: # ���� ����
		return render_template("main.html")

# Ű���� ��� page
@app.route('/register_keyword')
def registerKeyword():
	if('email' in session): # ���� ����
		return render_template('register_keyword.html', is_authenticated=True,
				email=session['email'], seq=session['seq'])
	else: # ���� ����
		return render_template("signin.html")

# Ű���� ���� page
@app.route('/manage_keyword')
def manageKeyword():
	if('email' in session): # ���� ����

		seq = session['seq']

		cur = g.db.cursor()
		cur.execute("SELECT * FROM keyword WHERE user_seq='%s' ORDER BY company, keyword" %(seq)) # ��ϵ� Ű���� ������ ��������
		rows = cur.fetchall()

		return render_template('manage_keyword.html', is_authenticated=True,
				email=session['email'], seq=session['seq'], rows=rows)
	else: # ���� ����
		return render_template("signin.html")

# ȸ�� ���� ���� page
@app.route('/manage_info')
def manageInfo():
	if('email' in session): # ���� ����
		return render_template('manage_info.html', is_authenticated=True,
				email=session['email'], seq=session['seq'])
	else: # ���� ����
		return render_template("signin.html")

# ȸ�� ���� page
@app.route('/signup')
def signUp():
	return render_template("signup.html")

# �α��� page
@app.route('/signin')
def signIn():
	return render_template("signin.html")

# �α��� ��û
@app.route('/signin/signin', methods=['POST'])
def signIn_signIn() :
	email = request.form.get("email")
	password = request.form.get("password")

	cur = g.db.cursor();
	cur.execute("SELECT * FROM user WHERE email='%s' AND password='%s'" %(email, password))	# email, ��й�ȣ Ȯ��
	rows = cur.fetchall()

	if len(rows) == 0 :	# �α��� ����
		return jsonify({"status": "fail"})	# �α��� ����
	else : # �α��� ����
		session['email'] = email
		session['password'] = password
		session['seq'] = rows[0][0]

		if('email' in session) : # ���� ����
			return jsonify({"status": "success"})
		else: # ���� ����
			return jsonify({"status": "fail"})	# �α��� ����

# ȸ������ ��û
@app.route('/signup/signup', methods=['POST'])
def signUp_signUp():

	email = request.form.get("email")
	password = request.form.get("password")
	birth = request.form.get("birth")
	sex = request.form.get("sex")

	cur = g.db.cursor()
	cur.execute("SELECT * FROM user WHERE email='%s'" %(email))	# email�� �ߺ��Ǵ��� Ȯ���ϱ� ���� query ���
	rows = cur.fetchall()

	if len(rows) == 0 :		# ȸ������ ����
		cur.execute("INSERT INTO user(email, password, birth, sex) VALUES('%s', '%s', '%s', '%s')" %(email, password, birth, sex)) 
		db.commit()
		return jsonify({"status": "success"})	
	else :			# ȸ������ ����
		return jsonify({"status": "fail"})

# �α׾ƿ�
@app.route("/logout", methods=["POST"])
def logOut() :
	session.clear() # ���� ����
	return jsonify({"status": "success"})

# Ű���� ���
@app.route("/register_keyword/insert", methods=["POST"])
def registerKeyword_insert() :
	seq = request.form.get("seq")
	keyword = request.form.get("keyword")
	company = request.form.get("company")

	# keyword table�� keyword �߰�
	cur = g.db.cursor()
	cur.execute("INSERT INTO keyword(user_seq, keyword, company) VALUES('%s', '%s', '%s')" %(seq, keyword, company)) 
	db.commit()

	return jsonify({"status": "success"})

# ȸ������ ������Ʈ
@app.route('/manage_info/update', methods=['POST'])
def manageInfo_update():

	seq = request.form.get("seq")
	password = request.form.get("password")
	birth = request.form.get("birth")
	sex = request.form.get("sex")

	cur = g.db.cursor()

	# ȸ������ ������Ʈ
	cur.execute("UPDATE user SET password = '%s', birth = '%s', sex = '%s' WHERE seq = '%s'" %(password, birth, sex, seq))
	db.commit()
	return jsonify({"status": "success"})	

# Ű���� ����
@app.route('/manage_keyword/delete', methods=['POST'])
def manageKeyword_delete():

	seq = request.form.get("seq")
	keyword = request.form.getlist("keyword[]")
	company = request.form.getlist("company[]")

	cur = g.db.cursor()

	i = 0

	# Ű���� ����
	for i in range(0, len(keyword)) :
		cur.execute("DELETE FROM keyword WHERE user_seq = '%s' AND keyword = '%s' AND company = '%s'" %(seq, keyword[i], company[i]))

	db.commit()

	return jsonify({"status": "success"})	

if __name__ == "__main__": 
	# app.run(debug=True)
	app.run(host="0.0.0.0", port=5000)
