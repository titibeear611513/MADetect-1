# 載入flask套件
from flask import Flask,render_template,request,redirect,session,url_for
from flask import jsonify
# 載入 pymongo、openai套件 (pip install openai)
import pymongo, openai

# mongodb連線(要先pip安裝) root是使用者名稱 root123是當初設定的密碼
client = pymongo.MongoClient("mongodb://root:root123@ac-nxhavl3-shard-00-00.kecqc4f.mongodb.net:27017,ac-nxhavl3-shard-00-01.kecqc4f.mongodb.net:27017,ac-nxhavl3-shard-00-02.kecqc4f.mongodb.net:27017/?ssl=true&replicaSet=atlas-10enrt-shard-0&authSource=admin&retryWrites=true&w=majority")

app = Flask(__name__)
app.secret_key="secret"

# 操作 madetect 資料庫
db = client.madetect

# 設定gpt apikey參數-----待修改路徑
with open('./static/doc/apikey.txt', 'r') as file:
    apikey = file.read().rstrip()

#首頁頁面
@app.route('/')
def homepage():
    return render_template('homepage.html')

#主功能頁面
@app.route('/home')
def home():
    if 'user_name' in session:
        return render_template('home.html')
    else:
        return redirect(url_for('login'))
    
@app.route('/madetect', methods=['GET', 'POST'])
def madetect():
    # 設定api金鑰
    openai.api_key = apikey

    # 接收前端資料
    input_ad=request.values.get('input_ad')
    print(input_ad)
    # 連接GPT<違反法條>---------內容待改
    result = openai.ChatCompletion.create(
        model = "gpt-3.5-turbo",
        messages = [
            {"role": "system", "content": "You are a helpful Legal Consultant."},
            #{"role": "user", "content": "Please learn about the relevant documents.\n" + lawadd2_text},
            {"role": "user", "content": "請告訴我此廣告詞是否違法" + input_ad},
        ]
    )
    # 存取GPT回應<違反法條>
    result_law = result['choices'][0]['message']['content']

    # 連接GPT<修改後廣告詞>---------內容待改
    result = openai.ChatCompletion.create(
        model = 'gpt-3.5-turbo',
        messages = [
            {"role": "system", "content": "You are a helpful Expert in the Marketing field."},
            #{"role": "user", "content": "Please learn about the relevant documents.\n" + lawadd2_text},
            {"role": "user", "content": input_ad + "請根據此廣告詞並參考下列有關它的敘述幫我修改它以避免違反法條: " + result_law},
        ]
    )
    # 存取GPT回應<修改後廣告詞>
    result_advice = result['choices'][0]['message']['content']

    '''
    # 根據接收到的資料跟資料庫互動，操作madetect資料庫的advertisement集合
    adcollection = db.advertisement
    
    # 讀取session中的user_name
    user_id=session['user_name']
    
    # 插入資料進資料庫
    adcollection.insert_one({
        'user_id': user_id,
        'ad_asked': input_ad,
        'result_law': result_law,
        'result_advice': result_advice
    })

    db.getCollection('user').aggregate([
        { "$match": {_id: ObjectID('\"'+user_id+'\"')}}
    ])'''
    
    response = {
        'result_law': result_law,
        'result_advice': result_advice
    }

    return jsonify(response)

#登入頁面
@app.route('/login')
def login_page():
    if 'user_name' in session:
          return redirect(url_for('home'))
    
    return render_template('userLogin.html')

#登入功能
@app.route('/login_function', methods=['POST'])
def login_function():
    user_email = request.form.get('user_email')
    user_password = request.form.get('user_password')

    # 根據接受到的資料跟資料庫互動，操作 madetect 資料庫的 user 集合
    collection = db.user

    # 檢查帳號密碼是否正確
    result = collection.find_one({
        "user_email": user_email,
        "user_password": user_password
    })
    
    if result is not None:
        # 登入成功
        session["user_name"] = result["user_name"]
        response = {'success': True}
    else:
        # 登入失敗
        response = {'success': False}
    
    return jsonify(response)

#內部主頁頁面
@app.route('/inner_homepage')
def inner_homepage():
	# 確認session裡是否已有資料(在/login_function中或登入失敗就不會將資料傳入session)

	if "user_name" in session:
		return render_template("inner_homepage.html")	
	else:
		return redirect("/")
		

#註冊頁面
@app.route('/signup')
def signup_page():
    if 'user_name' in session:
        return redirect(url_for('home'))
	
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

    #插入資料進資料庫
	collection.insert_one({
		"user_name":user_name,
		"user_email":user_email,
		"user_password":user_password
	})
	return render_template('userLogin.html')

# 登出
@app.route('/signout')
def signout():
    # 移除session中會員資訊
    del session['user_name']
    return redirect("/")

# 註冊功能判定帳號是否重複
@app.route('/check_email', methods=['POST'])
def check_email():
    user_email = request.form.get('email')
    
    # 根據接收到的資料與資料庫互動，操作 madetect 資料庫的 user 集合
    collection = db.user
    
    # 檢查是否有重複的 email
    result = collection.find_one({"user_email": user_email})
    
    if result is not None:
        response = {"exists": True}
    else:
        response = {"exists": False}
    
    return jsonify(response)


# 忘記密碼頁面
@app.route('/forgetpsw')
def forgetpsw():
	return render_template('userForget.html')

# 忘記密碼功能
@app.route('/forgetpsw_function', methods=['POST'])
def forgetpsw_function():
    # 接收前端資料
    user_name = request.values.get("user_name")
    user_email = request.values.get("user_email")

    # 根據接受到的資料跟資料庫互動，操作 madetect 資料庫的 user 集合
    collection = db.user

    # 檢查是否有 user 名字及郵件
    result = collection.find_one({
        "$and": [
            {"user_name": user_name},
            {"user_email": user_email}
        ]
    })

    if result is not None:
        session["user_email"] = result["user_email"]
        response = {"exists": True}
    else:
        response = {"exists": False}

    return jsonify(response)

#重設密碼頁面
@app.route('/reset')
def resetpsw():
	return render_template('resetPassword.html')

#重設密碼功能
@app.route('/reset_function', methods=['POST'])
def reset_function():

	# 接收前端資料
	user_password=request.values.get("user_password")

	# 根據接受到的資料跟資料庫互動，操作 madetect資料庫 的 user集合
	collection = db.user

	#更新user_password
	collection.update_one({
    	"user_email":session["user_email"]
	},{
    "$set":{
        "user_password":user_password
    	}
	})
	return render_template('userLogin.html')

#管理員登入頁面
@app.route('/adminlogin')
def adminlogin_page():
	return render_template('adminLogin.html')

#管理員忘記密碼頁面
@app.route('/adminforgetpsw')
def adminforgetpsw_page():
	return render_template('adminForget.html')

#管理員重設密碼頁面
@app.route('/adminresetpsw')
def adminresetpsw_pages():
	return render_template('adminReset.html')

#後端flask設定s
if __name__ == '__main__':
	app.run(host='0.0.0.0',port='5000',debug=True)