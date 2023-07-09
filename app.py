# 載入flask套件
from flask import Flask,render_template,request,redirect,session

# 載入 pymongo 套件
import pymongo

# mongodb連線(要先pip安裝) root是使用者名稱 root123是當初設定的密碼
client = pymongo.MongoClient("mongodb://root:root123@ac-nxhavl3-shard-00-00.kecqc4f.mongodb.net:27017,ac-nxhavl3-shard-00-01.kecqc4f.mongodb.net:27017,ac-nxhavl3-shard-00-02.kecqc4f.mongodb.net:27017/?ssl=true&replicaSet=atlas-10enrt-shard-0&authSource=admin&retryWrites=true&w=majority")

app = Flask(__name__)
app.secret_key="secret"

# 操作 madetect 資料庫
db = client.madetect   

#首頁頁面
@app.route('/')
def home():
    return render_template('homepage.html')

#登入頁面
@app.route('/login')
def login_page():
    return render_template('userLogin.html')

#登入功能
@app.route('/login_function', methods=['POST'])
def login_function():

	# 接收前端資料
	user_email=request.values.get("user_email")
	user_password=request.values.get("user_password")

	# 根據接受到的資料跟資料庫互動，操作 madetect資料庫 的 user集合
	collection = db.user

	# 檢查帳號密碼是否正確
	result=collection.find_one({
		"$and":[
			{"user_email":user_email},
			{"user_password":user_password}
		]
	})
	#登入失敗
	if result==None:
		return "登入失敗"
	#登入成功，在session紀錄會員資訊，導向到內部主頁
	session["user_name"]=result["user_name"]
	print(session["user_name"])
	return redirect("/inner_homepage")

#內部主頁頁面
@app.route('/inner_homepage')
def inner_homepage():
	if session["user_name"] == None:
		return redirect("/")	
	else:
		return render_template("inner_homepage.html")

#註冊頁面
@app.route('/signup')
def signup_page():

	return render_template('userSignup.html')

#註冊功能
@app.route('/signup_function', methods=['POST'])
def signup_function():

	# 接收前端資料
	user_name=request.values.get("user_name")
	user_email=request.values.get("user_email")
	user_password=request.values.get("user_password")

	# 根據接受到的資料跟資料庫互動，操作 madetect資料庫 的 user集合
	collection = db.user

	#檢查是否有重複帳號
	#---------------還沒做QQ

	#檢查再次確認密碼
	#---------------還沒做QQ

	#插入資料進資料庫
	collection.insert_one({
		"user_name":user_name,
		"user_email":user_email,
		"user_password":user_password
	})
	return render_template('userLogin.html')

#忘記密碼
@app.route('/forgetpsw')
def forgetpsw():
	return render_template('userForget.html')

#重設密碼
@app.route('/reset')
def resetpsw():
	return render_template('resetPassword.html')

#後端flask設定
if __name__ == '__main__':
	app.run(host='0.0.0.0',port='5000',debug=True)